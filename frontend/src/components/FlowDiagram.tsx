import { useState, useMemo } from 'react';

// ── Types ──────────────────────────────────────────────
interface StreamData { tonnage: number; grading: number[]; }

interface FlowNode {
  id: string; label: string; sublabel: string;
  x: number; y: number; w: number; h: number;
  type: 'feed' | 'crusher' | 'screen' | 'product' | 'splitter';
  streamKey?: string;
}

interface FlowEdge {
  from: string; to: string; label?: string; dashed?: boolean;
  fromPort?: 'top' | 'bottom' | 'left' | 'right';
  toPort?: 'top' | 'bottom' | 'left' | 'right';
}

interface Props {
  streams?: Record<string, StreamData>;
  products?: Record<string, number>;
  recircGt40?: number;
  recirc20_5?: number;
  highlightNode?: string | null;
  onNodeClick?: (nodeId: string) => void;
}

// ── Node→Stream mapping ────────────────────────────────
const NODE_STREAM_MAP: Record<string, string[]> = {
  feed:      ['raw_feed'],
  jaw:       ['jaw_product', 'jaw_feed'],
  grizzly:   [],
  prescreen: ['pre_screen_feed'],
  cone:      ['cone_product'],
  screen1:   [],
  vsi:       ['vsi_product'],
  screen2:   [],
  prod_40_80: [],
  prod_lt5:   [],
  prod_waste: [],
};

const PRODUCT_NODE_MAP: Record<string, string> = {
  prod_40_80: '40-80mm',
  prod_lt5:   '<5mm',
  prod_waste: '细砂回收',
};

// ── Layout ──────────────────────────────────────────────
const NODES: FlowNode[] = [
  { id: 'feed',    label: '原矿给料', sublabel: 'Raw Feed',       x: 30,  y: 60,  w: 130, h: 56, type: 'feed',    streamKey: 'raw_feed' },
  { id: 'grizzly', label: '棒条筛',   sublabel: 'Grizzly 150mm',   x: 210, y: 60,  w: 130, h: 56, type: 'screen' },
  { id: 'jaw',     label: '颚式破碎机', sublabel: 'Ci125 e=150',    x: 400, y: 40,  w: 140, h: 56, type: 'crusher', streamKey: 'jaw_product' },
  { id: 'prescreen',label:'预筛分',    sublabel: '2YKR3060 80mm',   x: 400, y: 170, w: 140, h: 56, type: 'screen',  streamKey: 'pre_screen_feed' },
  { id: 'cone',     label: '圆锥破碎机', sublabel: 'Ci225 e=40',    x: 620, y: 120, w: 140, h: 56, type: 'crusher', streamKey: 'cone_product' },
  { id: 'screen1', label: '第一筛分',   sublabel: '3YKR2472 40/20/5', x: 400, y: 300, w: 170, h: 60, type: 'screen' },
  { id: 'vsi',     label: '立轴冲击破', sublabel: 'PL9500 制砂',     x: 150, y: 430, w: 140, h: 56, type: 'crusher', streamKey: 'vsi_product' },
  { id: 'screen2', label: '第二筛分',   sublabel: '2YKR2472 5mm',    x: 430, y: 430, w: 150, h: 56, type: 'screen' },
  { id: 'prod_40_80', label: '40-80mm 粗骨料', sublabel: '成品',   x: 650, y: 230, w: 140, h: 50, type: 'product' },
  { id: 'prod_lt5',   label: '<5mm 机制砂',    sublabel: '成品',   x: 650, y: 410, w: 140, h: 50, type: 'product' },
  { id: 'prod_waste', label: '细砂回收',       sublabel: 'PL8500', x: 650, y: 500, w: 140, h: 50, type: 'product' },
];

const EDGES: FlowEdge[] = [
  { from: 'feed', to: 'grizzly', fromPort: 'right', toPort: 'left' },
  { from: 'grizzly', to: 'jaw', label: '>150', fromPort: 'top', toPort: 'left' },
  { from: 'jaw', to: 'prescreen', fromPort: 'bottom', toPort: 'top' },
  { from: 'grizzly', to: 'prescreen', label: '<150', fromPort: 'right', toPort: 'top' },
  { from: 'prescreen', to: 'cone', label: '>80', fromPort: 'right', toPort: 'left' },
  { from: 'prescreen', to: 'prod_40_80', label: '40-80', fromPort: 'bottom', toPort: 'left' },
  { from: 'cone', to: 'prescreen', label: '循环', dashed: true, fromPort: 'bottom', toPort: 'top' },
  { from: 'prescreen', to: 'screen1', label: '<40', fromPort: 'bottom', toPort: 'top' },
  { from: 'screen1', to: 'vsi', label: '40-20/20-5', fromPort: 'left', toPort: 'top' },
  { from: 'vsi', to: 'screen2', fromPort: 'right', toPort: 'left' },
  { from: 'screen2', to: 'vsi', label: '>5 循环', dashed: true, fromPort: 'top', toPort: 'bottom' },
  { from: 'screen2', to: 'prod_lt5', label: '<5', fromPort: 'right', toPort: 'left' },
  { from: 'screen1', to: 'prod_waste', label: '<5溢流', fromPort: 'right', toPort: 'left' },
];

// ── Helpers ────────────────────────────────────────────
function portPos(n: FlowNode, port: string) {
  const m: Record<string, {x:number;y:number}> = {
    top: {x:n.x+n.w/2, y:n.y}, bottom: {x:n.x+n.w/2, y:n.y+n.h},
    left: {x:n.x, y:n.y+n.h/2}, right: {x:n.x+n.w, y:n.y+n.h/2},
  };
  return m[port] || m.top;
}

function fmtTph(v: number) { return v >= 10 ? Math.round(v).toString() : v.toFixed(1); }
function fmtPct(v: number) { return v.toFixed(1) + '%'; }

const COLORS: Record<string, {bg:string;stroke:string;text:string}> = {
  feed:    {bg:'#1a1a2e',stroke:'#e2e8f0',text:'#e2e8f0'},
  crusher: {bg:'#1e1a2a',stroke:'#f59e0b',text:'#fcd34d'},
  screen:  {bg:'#1a1e2a',stroke:'#3b82f6',text:'#93c5fd'},
  product: {bg:'#1a2a1e',stroke:'#10b981',text:'#6ee7b7'},
  splitter:{bg:'#1a1a2e',stroke:'#6366f1',text:'#c4b5fd'},
};

// ── Component ──────────────────────────────────────────
export default function FlowDiagram({ streams, products, recircGt40, recirc20_5, highlightNode, onNodeClick }: Props) {
  const [hovered, setHovered] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const activeNode = highlightNode ?? selected;

  const nodeMap = useMemo(() => { const m=new Map<string,FlowNode>(); NODES.forEach(n=>m.set(n.id,n)); return m; }, []);

  const getStream = (nodeId: string): StreamData | null => {
    if (!streams) return null;
    const keys = NODE_STREAM_MAP[nodeId];
    if (keys) {
      for (const k of keys) { if (streams[k]) return streams[k]; }
    }
    // Fallback: partial match
    for (const [k, v] of Object.entries(streams)) {
      if (k.includes(nodeId) || nodeId.includes(k.replace(/_/g, ''))) return v;
    }
    return null;
  };

  const getProductTonnage = (nodeId: string): number | null => {
    if (!products) return null;
    const key = PRODUCT_NODE_MAP[nodeId];
    if (key && products[key] !== undefined) return products[key];
    return null;
  };

  // Derive tonnage for key streams
  const feedStream = streams?.['raw_feed'];
  const jawStream = streams?.['jaw_product'];
  const preStream = streams?.['pre_screen_feed'];
  const coneStream = streams?.['cone_product'];
  const vsiStream = streams?.['vsi_product'];

  return (
    <div style={{background:'#0f1117',borderRadius:12,border:'1px solid #1e293b',padding:24,overflow:'auto'}}>
      {/* Header */}
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
        <div>
          <h3 style={{margin:0,fontSize:15,fontWeight:600,color:'#e2e8f0'}}>工艺流程</h3>
          <p style={{margin:'4px 0 0',fontSize:12,color:'#64748b'}}>悬停/点击节点查看实时数据 · 虚线=循环回路</p>
        </div>
        <div style={{display:'flex',gap:14,fontSize:11,color:'#94a3b8'}}>
          {Object.entries(COLORS).map(([t,c])=>(
            <div key={t} style={{display:'flex',alignItems:'center',gap:5}}>
              <div style={{width:10,height:10,borderRadius:2,background:c.stroke}}/>
              <span>{t==='feed'?'给料':t==='crusher'?'破碎':t==='screen'?'筛分':t==='product'?'成品':'分流'}</span>
            </div>
          ))}
        </div>
      </div>

      <svg viewBox="0 0 830 620" style={{width:'100%',height:'auto',minWidth:830}}>
        <defs>
          <marker id="ar" viewBox="0 0 10 6" refX="9" refY="3" markerWidth="7" markerHeight="5" orient="auto">
            <path d="M0,0 L10,3 L0,6 Z" fill="#475569"/></marker>
          <marker id="ar-d" viewBox="0 0 10 6" refX="9" refY="3" markerWidth="7" markerHeight="5" orient="auto">
            <path d="M0,0 L10,3 L0,6 Z" fill="#818cf8"/></marker>
          <marker id="ar-h" viewBox="0 0 10 6" refX="9" refY="3" markerWidth="7" markerHeight="5" orient="auto">
            <path d="M0,0 L10,3 L0,6 Z" fill="#f59e0b"/></marker>
          <filter id="gl"><feGaussianBlur stdDeviation="3"/><feMerge><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>

        {/* ── Edges ── */}
        {EDGES.map((edge,i)=>{
          const fn=nodeMap.get(edge.from), tn=nodeMap.get(edge.to);
          if(!fn||!tn) return null;
          const fp=edge.fromPort||'right', tp=edge.toPort||'left';
          const from=portPos(fn,fp), to=portPos(tn,tp);
          let path: string;
          const dx=Math.abs(to.x-from.x), dy=Math.abs(to.y-from.y);
          if(dx<1||dy<1) path=`M${from.x},${from.y} L${to.x},${to.y}`;
          else if(fp==='bottom'&&tp==='top'){const my=(from.y+to.y)/2; path=`M${from.x},${from.y} L${from.x},${my} L${to.x},${my} L${to.x},${to.y}`;}
          else if(fp==='right'&&tp==='left'){const mx=(from.x+to.x)/2; path=`M${from.x},${from.y} L${mx},${from.y} L${mx},${to.y} L${to.x},${to.y}`;}
          else path=`M${from.x},${from.y} L${to.x},${to.y}`;

          const isRecirc=edge.dashed, isActive=activeNode&&(edge.from===activeNode||edge.to===activeNode);
          const lx=(from.x+to.x)/2, ly=(from.y+to.y)/2-8;

          return <g key={i}>
            <path d={path} fill="none" stroke={isActive?'#f59e0b':isRecirc?'#6366f1':'#334155'}
              strokeWidth={isActive?2:1.5} strokeDasharray={isRecirc?'6 4':undefined}
              markerEnd={isActive?'url(#ar-h)':isRecirc?'url(#ar-d)':'url(#ar)'}
              style={{transition:'stroke 0.2s'}}/>
            {edge.label&&(
              <text x={lx} y={ly} textAnchor="middle" fill={isRecirc?'#a5b4fc':'#64748b'}
                fontSize="10" fontFamily="ui-monospace,monospace" style={{pointerEvents:'none'}}>
                {edge.label}
              </text>
            )}
          </g>;
        })}

        {/* ── Nodes ── */}
        {NODES.map(node=>{
          const c=COLORS[node.type], isActive=activeNode===node.id, isHov=hovered===node.id;
          const stream=getStream(node.id);
          const pTonnage=getProductTonnage(node.id);

          // Dynamic sublabel: show t/h when data available
          let dynamicSub = node.sublabel;
          if (node.id==='feed' && feedStream) dynamicSub = `${fmtTph(feedStream.tonnage)} t/h`;
          else if (node.id==='jaw' && jawStream) dynamicSub = `${fmtTph(jawStream.tonnage)} t/h`;
          else if (node.id==='prescreen' && preStream) dynamicSub = `${fmtTph(preStream.tonnage)} t/h`;
          else if (node.id==='cone' && coneStream) dynamicSub = `${fmtTph(coneStream.tonnage)} t/h`;
          else if (node.id==='vsi' && vsiStream) dynamicSub = `${fmtTph(vsiStream.tonnage)} t/h`;
          else if (node.type==='product' && pTonnage !== null) dynamicSub = `${fmtPct(pTonnage)} 产率`;

          return <g key={node.id} transform={`translate(${node.x},${node.y})`}
            onClick={()=>{setSelected(selected===node.id?null:node.id);onNodeClick?.(node.id);}}
            onMouseEnter={()=>setHovered(node.id)} onMouseLeave={()=>setHovered(null)}
            style={{cursor:'pointer'}}>

            <rect width={node.w} height={node.h} rx={node.type==='product'?6:8}
              fill={isActive?'rgba(245,158,11,0.1)':c.bg}
              stroke={isActive?'#f59e0b':isHov?c.stroke:'#1e293b'}
              strokeWidth={isActive?2:isHov?1.5:1} filter={isActive?'url(#gl)':undefined}
              style={{transition:'all 0.2s'}}/>
            <rect width={node.w} height={3} rx={8} fill={c.stroke} opacity={isActive?1:0.7}/>

            <text x={node.w/2} y={node.h/2-(node.sublabel?2:-4)} textAnchor="middle"
              fill={isActive?'#fbbf24':c.text} fontSize={node.type==='product'?12:13}
              fontFamily="system-ui,sans-serif" fontWeight={600} style={{pointerEvents:'none'}}>
              {node.label}
            </text>
            <text x={node.w/2} y={node.h/2+16} textAnchor="middle"
              fill={isActive?'#d97706':stream?'#93c5fd':'#64748b'}
              fontSize="9.5" fontFamily="ui-monospace,monospace" style={{pointerEvents:'none'}}>
              {dynamicSub}
            </text>

            {/* Tooltip */}
            {(isHov||isActive) && stream && (
              <g transform={`translate(${node.w+8},4)`}>
                <rect x={0} y={0} width={130} height={52} rx={6} fill="#1e293b" stroke="#475569" strokeWidth={1}/>
                <text x={8} y={17} fill="#e2e8f0" fontSize="11" fontWeight={600} fontFamily="system-ui">{fmtTph(stream.tonnage)} t/h</text>
                <text x={8} y={33} fill="#94a3b8" fontSize="9.5" fontFamily="monospace">{`>150:${stream.grading[0]?.toFixed(1)} 150-80:${stream.grading[1]?.toFixed(1)}`}</text>
                <text x={8} y={48} fill="#94a3b8" fontSize="9.5" fontFamily="monospace">{`<5:${stream.grading[5]?.toFixed(1)} 40-20:${stream.grading[3]?.toFixed(1)} 20-5:${stream.grading[4]?.toFixed(1)}`}</text>
              </g>
            )}

            {/* Product node: show from products dict */}
            {node.type==='product' && pTonnage !== null && !stream && (isHov||isActive) && (
              <g transform={`translate(${node.w+8},4)`}>
                <rect x={0} y={0} width={100} height={28} rx={6} fill="#1e293b" stroke="#475569" strokeWidth={1}/>
                <text x={8} y={19} fill="#6ee7b7" fontSize="11" fontWeight={600} fontFamily="system-ui">产率 {fmtPct(pTonnage)}</text>
              </g>
            )}

            {isActive && <circle cx={node.w-6} cy={6} r={4} fill="#f59e0b">
              <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/></circle>}
          </g>;
        })}

        {/* ── Bottom info bar ── */}
        <g transform="translate(24,570)">
          {streams ? (
            <>
              <text fill="#64748b" fontSize="10" fontFamily="monospace">
                {feedStream ? `总处理量 ${fmtTph(feedStream.tonnage)} t/h` : `${Object.keys(streams).length} 个物料流`}
                {recircGt40 ? `  ·  碎石循环 ${recircGt40.toFixed(2)}x` : ''}
                {recirc20_5 ? `  ·  制砂循环 ${recirc20_5.toFixed(2)}x` : ''}
              </text>
              {products && (
                <text y={16} fill="#94a3b8" fontSize="10" fontFamily="monospace">
                  成品: {Object.entries(products).map(([k,v])=>`${k} ${fmtPct(v)}`).join('  ')}
                </text>
              )}
            </>
          ) : (
            <text fill="#475569" fontSize="10" fontFamily="monospace">运行计算后显示实时流量数据</text>
          )}
        </g>
      </svg>
    </div>
  );
}
