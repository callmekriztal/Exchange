import axios from 'axios';
import { Agent, Contract, Deliverable, LedgerEntry, Negotiation, Objective } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  async loginOrRegisterDemo(): Promise<string> {
    const email = 'trader@ai-economy.com';
    const password = 'SecureTraderPass123!';
    try {
      await client.post('/auth/register', { email, password });
    } catch {
      // User exists
    }
    const res = await client.post('/auth/login/json', { email, password });
    const token = res.data.access_token;
    localStorage.setItem('access_token', token);
    return token;
  },

  // Agents
  async getAgents(): Promise<Agent[]> {
    const res = await client.get<Agent[]>('/agents');
    return res.data;
  },

  async seedAgents(): Promise<Agent[]> {
    const res = await client.post<Agent[]>('/agents/seed');
    return res.data;
  },

  // Objectives
  async getObjectives(): Promise<Objective[]> {
    const res = await client.get<Objective[]>('/objectives');
    return res.data;
  },

  async getObjective(id: string): Promise<Objective> {
    const res = await client.get<Objective>(`/objectives/${id}`);
    return res.data;
  },

  async createObjective(title: string, description: string, max_budget_usd: number): Promise<Objective> {
    const res = await client.post<Objective>('/objectives', {
      title,
      description,
      max_budget_usd,
    });
    return res.data;
  },

  // Contracts & Negotiations
  async getContractsForObjective(objectiveId: string): Promise<Contract[]> {
    const res = await client.get<Contract[]>(`/contracts/objective/${objectiveId}`);
    return res.data;
  },

  async getNegotiation(subtaskId: string): Promise<Negotiation> {
    const res = await client.get<Negotiation>(`/contracts/negotiation/${subtaskId}`);
    return res.data;
  },

  // Payments (PayPal Orders v2)
  async createPayPalOrder(objectiveId: string, contractIds: string[]) {
    const res = await client.post('/payments/create-order', {
      objective_id: objectiveId,
      contract_ids: contractIds,
    });
    return res.data;
  },

  async capturePayPalOrder(paypalOrderId: string) {
    const res = await client.post('/payments/capture-order', {
      paypal_order_id: paypalOrderId,
    });
    return res.data;
  },

  // Deliverables
  async getDeliverable(contractId: string): Promise<Deliverable> {
    const res = await client.get<Deliverable>(`/deliverables/contract/${contractId}`);
    return res.data;
  },

  // Ledger
  async getLedgerEntries(): Promise<LedgerEntry[]> {
    const res = await client.get<LedgerEntry[]>('/ledger');
    return res.data;
  },
};
