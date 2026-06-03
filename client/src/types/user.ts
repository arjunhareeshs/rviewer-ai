export type UserRole = 'user' | 'admin' | 'recruiter';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
}

export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}

export interface LoginPayload {
  email: string;
  password?: string; // Optional if using OAuth in future, but usually required
}
