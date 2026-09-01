export type MessageRole = 'user' | 'assistant' | 'system';

export type MessageStatus = 
  | 'PENDING' 
  | 'COMPLETED' 
  | 'CLARIFICATION_REQUIRED' 
  | 'FAILED';

export interface ColumnDef {
  name: string;
  type_text: string;
  display_name: string;
}

export interface TableData {
  columns: ColumnDef[];
  rows: Record<string, any>[];
  total_row_count: number;
  truncated: boolean;
}

export interface KpiItem {
  label: string;
  value: string;
  change?: string;
  subtext?: string;
}

export interface EvidenceCard {
  title: string;
  value: string;
  description: string;
  metric_name: string;
}

export interface AgentAnalysisData {
  summary: string;
  findings: string[];
  evidence: EvidenceCard[];
  supporting_chart_type?: 'BAR' | 'LINE' | 'TABLE' | 'KPI';
}

export interface ClarificationOption {
  id: string;
  label: string;
  value: string;
}

export interface ClarificationPayload {
  prompt: string;
  options: ClarificationOption[];
}

export interface QueryAttachment {
  query_id: string;
  query_text?: string;
  source_object: string;
  target_metric?: string;
  table_data?: TableData;
  recommended_visualization?: 'BAR' | 'LINE' | 'TABLE' | 'KPI' | 'SCATTER';
  kpis?: KpiItem[];
}

export interface Message {
  message_id: string;
  role: MessageRole;
  content: string;
  status: MessageStatus;
  created_at: string;
  attachment?: QueryAttachment;
  clarification?: ClarificationPayload;
  agent_analysis?: AgentAnalysisData;
  follow_up_suggestions?: string[];
  client_request_id?: string;
}

export interface Conversation {
  conversation_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message: string;
  message_count: number;
}

export interface ApiError {
  code: string;
  message: string;
  status_code: number;
}
