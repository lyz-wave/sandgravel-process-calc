import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export interface BalanceRequest {
  config_name?: string;
  feed_grading?: number[];
  system_throughput?: number;
}

export interface FlowNode {
  id: string; label: string; sublabel: string;
  x: number; y: number; w: number; h: number;
  type: 'feed' | 'crusher' | 'screen' | 'product' | 'splitter';
  streamKey?: string;
}

export interface FlowEdge {
  from: string; to: string; label?: string; dashed?: boolean;
  fromPort?: 'top' | 'bottom' | 'left' | 'right';
  toPort?: 'top' | 'bottom' | 'left' | 'right';
}

export interface FlowStructure {
  nodes: FlowNode[];
  edges: FlowEdge[];
  streamMap: Record<string, string[]>;
  productMap: Record<string, string>;
}

export interface BalanceResponse {
  streams: Record<string, { tonnage: number; grading: number[] }>;
  equipment: Array<{ model: string; quantity: number; unit_capacity: number; load_factor: number }>;
  products?: Record<string, number>;
  recirculation_gt40?: number;
  recirculation_20_5?: number;
  iterations: number;
  convergence_error: number;
  config_name?: string;
  flow_structure?: FlowStructure;
}

export interface ConfigDefaults {
  config_name: string;
  system_throughput: number;
  feed_grading: number[];
}

export async function getConfigDefaults(name: string): Promise<ConfigDefaults> {
  const { data } = await api.get('/balance/config-defaults', { params: { name } });
  return data;
}

export async function calculateBalance(req: BalanceRequest): Promise<BalanceResponse> {
  const { data } = await api.post('/balance/calculate', req);
  return data;
}

export async function getOptions() {
  const { data } = await api.get('/options');
  return data;
}

export async function exportToExcel(result: BalanceResponse): Promise<void> {
  const { data } = await api.post('/io/export-excel', result, { responseType: 'blob' });
  const url = URL.createObjectURL(data);
  const a = document.createElement('a');
  a.href = url;
  a.download = `balance_result_${new Date().toISOString().slice(0, 10)}.xlsx`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function exportToPdf(result: BalanceResponse, type: 'full' | 'calculation' | 'equipment' = 'full'): Promise<void> {
  const { data } = await api.post(`/io/export-pdf?type=${type}`, result, { responseType: 'blob' });
  const url = URL.createObjectURL(data);
  const a = document.createElement('a');
  a.href = url;
  const suffix = type === 'equipment' ? 'equipment' : type === 'calculation' ? 'calc' : 'report';
  a.download = `sandgravel_${suffix}_${new Date().toISOString().slice(0, 10)}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
