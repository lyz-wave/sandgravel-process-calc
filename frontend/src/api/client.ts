import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export interface BalanceRequest {
  config_name?: string;
  feed_grading?: number[];
  system_throughput?: number;
}

export interface BalanceResponse {
  streams: Record<string, { tonnage: number; grading: number[] }>;
  equipment: Array<{ model: string; quantity: number; unit_capacity: number; load_factor: number }>;
  products?: Record<string, number>;
  recirculation_gt40?: number;
  recirculation_20_5?: number;
  iterations: number;
  convergence_error: number;
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
