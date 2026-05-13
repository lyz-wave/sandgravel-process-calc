import { useState, useMemo } from 'react';
import type { FlowNode, FlowEdge, FlowStructure } from '../api/client';

interface StreamData { tonnage: number; grading: number[]; }

interface Props {
  streams?: Record<string, StreamData>;
  products?: Record<string, number>;
  recircGt40?: number;
  recirc20_5?: number;
  flowStructure?: FlowStructure;
  highlightNode?: string | null;
  onNodeClick?: (nodeId: string) => void;
}

function portPos(n: FlowNode, port: string) {
  const m: Record<string, { x: number; y: number }> = {
    top: { x: n.x + n.w / 2, y: n.y },
    bottom: { x: n.x + n.w / 2, y: n.y + n.h },
    left: { x: n.x, y: n.y + n.h / 2 },
    right: { x: n.x + n.w, y: n.y + n.h / 2 },
  };
  return m[port] || m.top;
}

function fmtTph(v: number) { return v >= 10 ? Math.round(v).toString() : v.toFixed(1); }
function fmtPct(v: number) { return v.toFixed(1) + '%'; }

const TYPE_COLORS: Record<string, { stroke: string; text: string; bg: string }> = {
  feed:    { stroke: '#94a3b8', text: '#cbd5e1', bg: '#0f1419' },
  crusher: { stroke: '#f59e0b', text: '#fcd34d', bg: '#14100a' },
  screen:  { stroke: '#3b82f6', text: '#93c5fd', bg: '#0a1018' },
  product: { stroke: '#10b981', text: '#6ee7b7', bg: '#0a1410' },
  splitter:{ stroke: '#818cf8', text: '#c4b5fd', bg: '#0f0f18' },
};

export default function FlowDiagram({ streams, products, recircGt40, recirc20_5, flowStructure, highlightNode, onNodeClick }: Props) {
  const [hovered, setHovered] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const activeNode = highlightNode ?? selected;

  const nodes: FlowNode[] = flowStructure?.nodes ?? [];
  const edges: FlowEdge[] = flowStructure?.edges ?? [];
  const streamMap: Record<string, string[]> = flowStructure?.streamMap ?? {};
  const productMap: Record<string, string> = flowStructure?.productMap ?? {};

  const nodeMap = useMemo(() => {
    const m = new Map<string, FlowNode>();
    nodes.forEach(n => m.set(n.id, n));
    return m;
  }, [nodes]);

  const getStream = (nodeId: string): StreamData | null => {
    if (!streams) return null;
    const keys = streamMap[nodeId];
    if (keys) {
      for (const k of keys) { if (streams[k]) return streams[k]; }
    }
    for (const [k, v] of Object.entries(streams)) {
      if (k.includes(nodeId) || nodeId.includes(k.replace(/_/g, ''))) return v;
    }
    return null;
  };

  const getProductTonnage = (nodeId: string): number | null => {
    if (!products) return null;
    const key = productMap[nodeId];
    if (key && products[key] !== undefined) return products[key];
    return null;
  };

  const feedStream = streams?.['raw_feed'];
  const jawStream = streams?.['jaw_product'];
  const preStream = streams?.['pre_screen_feed'];
  const coneStream = streams?.['cone_product'];
  const vsiStream = streams?.['vsi_product'];

  // Compute SVG viewBox from node extents
  const viewBox = useMemo(() => {
    if (nodes.length === 0) return '0 0 830 620';
    let maxX = 0, maxY = 0;
    for (const n of nodes) {
      if (n.x + n.w > maxX) maxX = n.x + n.w;
      if (n.y + n.h > maxY) maxY = n.y + n.h;
    }
    return `0 0 ${Math.max(maxX + 170, 830)} ${Math.max(maxY + 60, 620)}`;
  }, [nodes]);

  return (
    <div className="flow-container">
      <div className="flow-header">
        <div>
          <div className="flow-title">工艺流程</div>
          <div className="flow-hint">悬停节点查看实时数据 · 虚线 = 循环回路 · 点击节点高亮关联边</div>
        </div>
        <div className="flow-legend">
          {Object.entries(TYPE_COLORS).map(([t, c]) => (
            <div key={t} className="flow-legend-item">
              <div className="flow-legend-dot" style={{ background: c.stroke }} />
              <span>{t === 'feed' ? '给料' : t === 'crusher' ? '破碎' : t === 'screen' ? '筛分' : t === 'product' ? '成品' : '分流'}</span>
            </div>
          ))}
        </div>
      </div>

      <svg viewBox={viewBox} style={{ width: '100%', height: 'auto', minWidth: 830 }}>
        <defs>
          <marker id="ar" viewBox="0 0 10 6" refX="9" refY="3" markerWidth="6" markerHeight="4" orient="auto">
            <path d="M0,0 L10,3 L0,6 Z" fill="#2a3a4e" />
          </marker>
          <marker id="ar-d" viewBox="0 0 10 6" refX="9" refY="3" markerWidth="6" markerHeight="4" orient="auto">
            <path d="M0,0 L10,3 L0,6 Z" fill="#6366f1" />
          </marker>
          <marker id="ar-h" viewBox="0 0 10 6" refX="9" refY="3" markerWidth="6" markerHeight="4" orient="auto">
            <path d="M0,0 L10,3 L0,6 Z" fill="#f59e0b" />
          </marker>
          <filter id="gl-amber" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <filter id="gl-node" x="-30%" y="-30%" width="160%" height="160%">
            <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="rgba(245,158,11,0.3)" />
          </filter>
          <linearGradient id="grad-amber" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.02" />
          </linearGradient>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e2d3d" strokeWidth="0.3" opacity="0.4" />
          </pattern>
        </defs>

        <rect x="0" y="0" width="1000" height="700" fill="url(#grid)" />

        {/* ── Edges ── */}
        {edges.map((edge, i) => {
          const fn = nodeMap.get(edge.from);
          const tn = nodeMap.get(edge.to);
          if (!fn || !tn) return null;
          const fp = edge.fromPort || 'right';
          const tp = edge.toPort || 'left';
          const from = portPos(fn, fp);
          const to = portPos(tn, tp);

          let path: string;
          const dx = Math.abs(to.x - from.x);
          const dy = Math.abs(to.y - from.y);

          if (dx < 1 || dy < 1) {
            path = `M${from.x},${from.y} L${to.x},${to.y}`;
          } else if (fp === 'bottom' && tp === 'top') {
            const my = (from.y + to.y) / 2;
            path = `M${from.x},${from.y} L${from.x},${my} L${to.x},${my} L${to.x},${to.y}`;
          } else if (fp === 'right' && tp === 'left') {
            const mx = (from.x + to.x) / 2;
            path = `M${from.x},${from.y} L${mx},${from.y} L${mx},${to.y} L${to.x},${to.y}`;
          } else {
            path = `M${from.x},${from.y} L${to.x},${to.y}`;
          }

          const isRecirc = edge.dashed;
          const isActive = activeNode && (edge.from === activeNode || edge.to === activeNode);
          const lx = (from.x + to.x) / 2;
          const ly = (from.y + to.y) / 2 - 8;

          return (
            <g key={i}>
              {isActive && (
                <path d={path} fill="none" stroke="#f59e0b" strokeWidth={4} opacity="0.4"
                  strokeDasharray={isRecirc ? '6 4' : undefined} filter="url(#gl-amber)" />
              )}
              <path d={path} fill="none"
                stroke={isActive ? '#f59e0b' : isRecirc ? '#6366f1' : '#2a3a4e'}
                strokeWidth={isActive ? 2 : 1.3}
                strokeDasharray={isRecirc ? '6 4' : undefined}
                markerEnd={isActive ? 'url(#ar-h)' : isRecirc ? 'url(#ar-d)' : 'url(#ar)'}
                style={{ transition: 'stroke 0.25s, strokeWidth 0.25s' }}
              />
              {edge.label && (
                <text x={lx} y={ly} textAnchor="middle"
                  fill={isRecirc ? '#a5b4fc' : '#4a5568'}
                  fontSize="9" fontFamily="var(--font-mono)">
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}

        {/* ── Nodes ── */}
        {nodes.map(node => {
          const c = TYPE_COLORS[node.type] || TYPE_COLORS.feed;
          const isActive = activeNode === node.id;
          const isHov = hovered === node.id;
          const stream = getStream(node.id);
          const pTonnage = getProductTonnage(node.id);
          const hasData = !!streams;

          let dynamicSub = node.sublabel;
          if (node.id === 'feed' && feedStream) dynamicSub = `${fmtTph(feedStream.tonnage)} t/h`;
          else if (node.id === 'jaw' && jawStream) dynamicSub = `${fmtTph(jawStream.tonnage)} t/h`;
          else if (node.id === 'prescreen' && preStream) dynamicSub = `${fmtTph(preStream.tonnage)} t/h`;
          else if (node.id === 'cone' && coneStream) dynamicSub = `${fmtTph(coneStream.tonnage)} t/h`;
          else if (node.id === 'vsi' && vsiStream) dynamicSub = `${fmtTph(vsiStream.tonnage)} t/h`;
          else if (node.type === 'product' && pTonnage !== null) dynamicSub = `${fmtPct(pTonnage)} 产率`;

          return (
            <g key={node.id} transform={`translate(${node.x},${node.y})`}
              onClick={() => { setSelected(selected === node.id ? null : node.id); onNodeClick?.(node.id); }}
              onMouseEnter={() => setHovered(node.id)}
              onMouseLeave={() => setHovered(null)}
              style={{ cursor: 'pointer' }}
            >
              {isActive && (
                <rect x="-3" y="-3" width={node.w + 6} height={node.h + 6}
                  rx={node.type === 'product' ? 8 : 10} fill="none"
                  stroke="#f59e0b" strokeWidth="2" opacity="0.5"
                  filter="url(#gl-amber)" />
              )}
              <rect width={node.w} height={node.h}
                rx={node.type === 'product' ? 6 : 8}
                fill={isActive ? 'url(#grad-amber)' : c.bg}
                stroke={isActive ? '#f59e0b' : isHov ? c.stroke : '#1e2d3d'}
                strokeWidth={isActive ? 1.5 : isHov ? 1.2 : 1}
                filter={isActive ? 'url(#gl-node)' : undefined}
                style={{ transition: 'all 0.2s' }}
              />
              <rect width={node.w} height={3} rx={8}
                fill={c.stroke} opacity={isActive ? 1 : 0.6}
                style={{ transition: 'opacity 0.2s' }}
              />
              <text x={node.w / 2} y={node.h / 2 - (node.sublabel ? 2 : 4)}
                textAnchor="middle"
                fill={isActive ? '#fbbf24' : c.text}
                fontSize={node.type === 'product' ? 12 : 13}
                fontFamily="var(--font-sans)" fontWeight={600}
                style={{ pointerEvents: 'none', transition: 'fill 0.2s' }}
              >
                {node.label}
              </text>
              <text x={node.w / 2} y={node.h / 2 + 16}
                textAnchor="middle"
                fill={isActive ? '#d97706' : hasData && stream ? '#93c5fd' : '#4a5568'}
                fontSize="9.5" fontFamily="var(--font-mono)"
                style={{ pointerEvents: 'none', transition: 'fill 0.2s' }}
              >
                {dynamicSub}
              </text>
              {isActive && (
                <circle cx={node.w - 6} cy={6} r={4} fill="#f59e0b">
                  <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite" />
                </circle>
              )}
            </g>
          );
        })}

        {/* ── Tooltips (always on top) ── */}
        {nodes.map(node => {
          const isHov = hovered === node.id;
          const isActive = activeNode === node.id;
          if (!isHov && !isActive) return null;

          const c = TYPE_COLORS[node.type] || TYPE_COLORS.feed;
          const stream = getStream(node.id);
          const pTonnage = getProductTonnage(node.id);

          if (stream) {
            const tw = 190, th = 70;
            const flip = node.x + node.w + 8 + tw > 1000;
            const tx = flip ? node.x - 8 - tw : node.x + node.w + 8;
            const ty = node.y + 4;

            return (
              <g key={`tt-${node.id}`} transform={`translate(${tx},${ty})`} style={{ pointerEvents: 'none' }}>
                <rect x={0} y={0} width={tw} height={th} rx={5} fill="#141c26" stroke="#2a3a4e" strokeWidth={1} filter="url(#gl-node)" />
                <rect x={0} y={0} width={tw} height={18} rx={5} fill="rgba(0,0,0,0.3)" />
                <rect x={0} y={9} width={tw} height={9} fill="rgba(0,0,0,0.3)" />
                <text x={8} y={13} fill={c.stroke} fontSize="10" fontWeight={600} fontFamily="var(--font-sans)">
                  {fmtTph(stream.tonnage)} t/h
                </text>
                <text x={8} y={32} fill="#8896a8" fontSize="9" fontFamily="var(--font-mono)">
                  {`>150 ${stream.grading[0]?.toFixed(1)}%  ·  150-80 ${stream.grading[1]?.toFixed(1)}%`}
                </text>
                <text x={8} y={48} fill="#8896a8" fontSize="9" fontFamily="var(--font-mono)">
                  {`80-40 ${stream.grading[2]?.toFixed(1)}%  ·  40-20 ${stream.grading[3]?.toFixed(1)}%`}
                </text>
                <text x={8} y={64} fill="#8896a8" fontSize="9" fontFamily="var(--font-mono)">
                  {`20-5 ${stream.grading[4]?.toFixed(1)}%  ·  <5 ${stream.grading[5]?.toFixed(1)}%`}
                </text>
              </g>
            );
          }

          if (node.type === 'product' && pTonnage !== null) {
            const tw = 125, th = 28;
            const flip = node.x + node.w + 8 + tw > 1000;
            const tx = flip ? node.x - 8 - tw : node.x + node.w + 8;
            const ty = node.y + 4;

            return (
              <g key={`tt-${node.id}`} transform={`translate(${tx},${ty})`} style={{ pointerEvents: 'none' }}>
                <rect x={0} y={0} width={tw} height={th} rx={5} fill="#141c26" stroke="#2a3a4e" strokeWidth={1} />
                <text x={8} y={19} fill="#6ee7b7" fontSize="11" fontWeight={600} fontFamily="var(--font-sans)">
                  产率 {fmtPct(pTonnage)}
                </text>
              </g>
            );
          }

          return null;
        })}

        {/* ── Bottom info bar ── */}
        <g transform="translate(24, 570)">
          {streams ? (
            <>
              <text fill="#4a5568" fontSize="10" fontFamily="var(--font-mono)">
                {feedStream ? `总处理量 ${fmtTph(feedStream.tonnage)} t/h` : `${Object.keys(streams).length} 个物料流`}
                {recircGt40 ? (
                  <tspan fill="#a5b4fc">  ·  碎石循环 <tspan fill="#c4b5fd" fontWeight={500}>{recircGt40.toFixed(2)}x</tspan></tspan>
                ) : null}
                {recirc20_5 ? (
                  <tspan fill="#a5b4fc">  ·  制砂循环 <tspan fill="#c4b5fd" fontWeight={500}>{recirc20_5.toFixed(2)}x</tspan></tspan>
                ) : null}
              </text>
              {products && (
                <text y={16} fill="#64748b" fontSize="9.5" fontFamily="var(--font-mono)">
                  成品: {Object.entries(products).map(([k, v]) => `${k} ${fmtPct(v)}`).join('  |  ')}
                </text>
              )}
            </>
          ) : (
            <text fill="#2a3a4e" fontSize="10" fontFamily="var(--font-mono)">
              运行计算后显示实时流量数据
            </text>
          )}
        </g>
      </svg>
    </div>
  );
}
