import { useRef, useState } from 'react';
import axios from 'axios';
import { BalanceResponse } from '../api/client';

interface Props {
  onImported: (data: BalanceResponse) => void;
}

export default function ImportButton({ onImported }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      const form = new FormData();
      form.append('file', file);
      const { data } = await axios.post('/api/io/import-excel', form);
      onImported(data as BalanceResponse);
    } catch (err: any) {
      alert('导入失败: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  return (
    <>
      <input ref={fileRef} type="file" accept=".xlsx,.xls"
        onChange={handleFile} style={{ display: 'none' }} />
      <button
        className="btn btn-ghost"
        onClick={() => fileRef.current?.click()}
        disabled={loading}
      >
        <span className="btn-icon">↑</span>
        {loading ? '导入中...' : '导入 Excel'}
      </button>
    </>
  );
}
