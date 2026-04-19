/**
 * AP2 Telegram-Verknüpfungs-API.
 *
 * Endpoints unter /api/v1/user/exam-trainer/ap2/telegram/*
 */

import http from '@/infrastructure/api/http'

const BASE = '/user/exam-trainer/ap2/telegram'

export interface TelegramLinkCode {
  code: string
  expires_at: string
  bot_username: string
  instruction: string
}

export interface TelegramStatus {
  linked: boolean
  bot_username: string
}

export async function getTelegramStatus(): Promise<TelegramStatus> {
  const res = await http.get<TelegramStatus>(`${BASE}/status`)
  return res.data
}

export async function generateTelegramLinkCode(): Promise<TelegramLinkCode> {
  const res = await http.post<TelegramLinkCode>(`${BASE}/link-code`)
  return res.data
}

export async function unlinkTelegram(): Promise<void> {
  await http.delete(`${BASE}/link`)
}
