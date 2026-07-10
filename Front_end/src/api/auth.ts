import request from '@/utils/request'
import type { AuthResponse, LoginPayload, RegisterPayload, User } from '@/types/auth'

export function login(data: LoginPayload): Promise<AuthResponse> {
  return request.post('/auth/login', data, { skipLoading: true } as any)
}

export function register(data: RegisterPayload): Promise<any> {
  return request.post('/auth/register', data, { skipLoading: true } as any)
}

export function getMe(): Promise<User> {
  return request.get('/auth/me', { skipLoading: true } as any)
}