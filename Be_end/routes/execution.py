import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from database import get_db, SessionLocal
from models import User, Workflow, WorkflowRun
from schemas import WorkflowRunRequest, WorkflowRunSummary, WorkflowRunDetail
from security import get_current_user
from workflow_executor import build_execution_order, execute_node, now_iso, _node_label

router = APIRouter(prefix="/workflows", tags=["workflow-execution"])


def _sse(event_type: str, payload: dict) -> str:
    return f"data: {json.dumps({'type': event_type, **payload}, ensure_ascii=False)}\n\n"


def _get_workflow(db: Session, wf_id: int, user_id: int) -> Workflow:
    wf = db.query(Workflow).filter(
        Workflow.id == wf_id,
        Workflow.user_id == user_id,
    ).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.post("/{wf_id}/run")
def run_workflow(
    wf_id: int,
    body: WorkflowRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    wf = _get_workflow(db, wf_id, user_id)
    graph = body.graph_json if body.graph_json else (wf.graph_json or {})
    input_data = body.input if body.input is not None else {}

    run = WorkflowRun(
        workflow_id=wf_id,
        user_id=user_id,
        status="running",
        input_json=input_data,
        logs_json=[],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    run_id = run.id

    def generate():
        logs: list[dict] = []
        last_output = input_data

        def add_log(level: str, message: str, node_id: str | None = None):
            entry = {
                "time": now_iso(),
                "level": level,
                "message": message,
                "node_id": node_id,
            }
            logs.append(entry)
            return _sse("log", entry)

        yield _sse("run_start", {"run_id": run_id, "workflow_id": wf_id})

        try:
            nodes = graph.get("nodes", [])
            edges = graph.get("edges", [])
            order = build_execution_order(nodes, edges)
            context: dict = {"variables": {}, "user_id": user_id}

            yield add_log("info", f"工作流开始执行，共 {len(order)} 个节点")

            for node in order:
                nid = node["id"]
                label = _node_label(node)
                yield _sse("node_start", {
                    "node_id": nid,
                    "node_type": node.get("type"),
                    "label": label,
                })
                yield add_log("info", f"正在执行节点: {label}", nid)

                try:
                    output = execute_node(node, last_output, context)
                    context["variables"][nid] = output
                    last_output = output

                    trace = context.pop("last_trace", None)
                    if trace and trace.get("enableTracing"):
                        strategies = trace.get("strategiesApplied") or {}
                        rag_n = strategies.get("ragChunksInjected", 0)
                        rag_hint = f" | RAG注入={rag_n}段" if rag_n else ""
                        yield add_log(
                            "info",
                            (
                                f"模型配置生效: [{trace['profileName']}] "
                                f"{trace['modelId']} @ {trace['baseUrl']} | "
                                f"延迟 {trace['latencyMs']}ms | "
                                f"Agent={trace['agentMode']} | "
                                f"策略={strategies.get('historyStrategy')}"
                                f"{rag_hint}"
                            ),
                            nid,
                        )
                        usage = trace.get("usage") or {}
                        if usage.get("prompt_tokens") is not None:
                            yield add_log(
                                "debug",
                                f"Token: prompt={usage.get('prompt_tokens')} completion={usage.get('completion_tokens')}",
                                nid,
                            )

                    yield _sse("node_success", {
                        "node_id": nid,
                        "output": output,
                        "trace": trace,
                    })
                    yield add_log("success", f"节点完成: {label}", nid)
                except Exception as e:
                    yield _sse("node_failed", {
                        "node_id": nid,
                        "error": str(e),
                    })
                    yield add_log("error", f"节点失败: {label} — {e}", nid)

                    save_db = SessionLocal()
                    try:
                        r = save_db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
                        if r:
                            r.status = "failed"
                            r.output_json = {"error": str(e), "node_id": nid}
                            r.logs_json = logs
                            r.finished_at = datetime.now()
                            save_db.commit()
                    finally:
                        save_db.close()

                    yield _sse("done", {
                        "run_id": run_id,
                        "status": "failed",
                        "output": {"error": str(e)},
                    })
                    return

            save_db = SessionLocal()
            try:
                r = save_db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
                if r:
                    r.status = "success"
                    r.output_json = last_output
                    r.logs_json = logs
                    r.finished_at = datetime.now()
                    save_db.commit()
            finally:
                save_db.close()

            yield add_log("info", "工作流执行完成")
            yield _sse("done", {
                "run_id": run_id,
                "status": "success",
                "output": last_output,
            })

        except Exception as e:
            yield _sse("error", {"content": str(e)})
            save_db = SessionLocal()
            try:
                r = save_db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
                if r:
                    r.status = "failed"
                    r.output_json = {"error": str(e)}
                    r.logs_json = logs
                    r.finished_at = datetime.now()
                    save_db.commit()
            finally:
                save_db.close()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/{wf_id}/runs", response_model=List[WorkflowRunSummary])
def list_workflow_runs(
    wf_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_workflow(db, wf_id, current_user.id)
    runs = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.workflow_id == wf_id, WorkflowRun.user_id == current_user.id)
        .order_by(WorkflowRun.started_at.desc())
        .limit(50)
        .all()
    )
    return runs


@router.get("/{wf_id}/runs/{run_id}", response_model=WorkflowRunDetail)
def get_workflow_run(
    wf_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_workflow(db, wf_id, current_user.id)
    run = db.query(WorkflowRun).filter(
        WorkflowRun.id == run_id,
        WorkflowRun.workflow_id == wf_id,
        WorkflowRun.user_id == current_user.id,
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
