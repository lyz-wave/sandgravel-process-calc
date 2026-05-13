interface Props {
  streams: Record<string, { tonnage: number; grading: number[] }>;
}

const SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5'];

export default function BalanceTable({ streams }: Props) {
  const entries = Object.entries(streams);
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>物料流</th>
          <th>t/h</th>
          {SIZE_LABELS.map(l => <th key={l}>{l}</th>)}
        </tr>
      </thead>
      <tbody>
        {entries.map(([name, stream]) => (
          <tr key={name}>
            <td>{name}</td>
            <td className="col-tonnage">{stream.tonnage.toFixed(1)}</td>
            {stream.grading.map((v, i) => (
              <td key={i}>{v.toFixed(2)}%</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
