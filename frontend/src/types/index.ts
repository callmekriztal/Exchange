export interface AgentService {
  id: string;
  agent_id: string;
  service_name: string;
  service_category: string;
  description: string;
  pricing_type: string;
  base_price_usd: number;
  min_price_usd: number;
  max_price_usd: number;
  is_available: boolean;
}

export interface Agent {
  id: string;
  name: string;
  agent_type: 'buyer' | 'research' | 'analysis' | 'report';
  description?: string;
  capabilities: string[];
  pricing_policy: Record<string, any>;
  is_active: boolean;
  services: AgentService[];
}

export interface Subtask {
  id: string;
  objective_id: string;
  assigned_seller_id?: string;
  title: string;
  description: string;
  service_type: string;
  allocated_budget_usd: number;
  agreed_price_usd?: number;
  sequence_order: number;
  status: string;
  input_payload: Record<string, any>;
  created_at: string;
}

export interface Objective {
  id: string;
  user_id: string;
  title: string;
  description: string;
  max_budget_usd: number;
  total_spent_usd: number;
  status: 'draft' | 'planning' | 'negotiating' | 'awaiting_payment' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  subtasks: Subtask[];
}

export interface NegotiationRound {
  id: string;
  round_number: number;
  speaker_agent_id: string;
  action: 'offer' | 'counter_offer' | 'accept' | 'reject';
  proposed_price_usd: number;
  rationale: string;
  created_at: string;
}

export interface Negotiation {
  id: string;
  subtask_id: string;
  buyer_agent_id: string;
  seller_agent_id: string;
  buyer_opening_offer_usd: number;
  seller_opening_ask_usd: number;
  final_agreed_price_usd?: number;
  max_rounds: number;
  current_round: number;
  status: string;
  rounds: NegotiationRound[];
}

export interface Contract {
  id: string;
  subtask_id: string;
  buyer_agent_id: string;
  seller_agent_id: string;
  negotiation_id: string;
  agreed_amount_usd: number;
  terms_and_conditions: Record<string, any>;
  status: 'draft' | 'pending_payment' | 'funded' | 'active' | 'completed' | 'disputed';
  subtask?: Subtask;
  created_at: string;
  signed_at?: string;
}

export interface Evaluation {
  id: string;
  deliverable_id: string;
  evaluator_agent_id: string;
  rubric_scores: Record<string, any>;
  score: number;
  is_accepted: boolean;
  feedback: string;
  evaluated_at: string;
}

export interface Deliverable {
  id: string;
  contract_id: string;
  seller_agent_id: string;
  artifact_type: string;
  content: Record<string, any>;
  checksum: string;
  execution_duration_ms: number;
  submitted_at: string;
  evaluation?: Evaluation;
}

export interface LedgerEntry {
  id: string;
  payment_id?: string;
  contract_id?: string;
  debit_account: string;
  credit_account: string;
  amount_usd: number;
  entry_type: string;
  description: string;
  created_at: string;
}
