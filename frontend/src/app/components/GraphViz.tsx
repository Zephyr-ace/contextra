'use client';

import React, { useCallback, useState, useRef } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  EdgeLabelRenderer,
  Handle,
  Position,
  getStraightPath,
  useReactFlow,
  type EdgeProps,
  type EdgeTypes,
  type Node,
  type Edge,
} from 'reactflow';
import 'reactflow/dist/style.css';

/* ---------------------------- Custom Node ---------------------------------- */

const CustomNode = ({ data }: { data: { label: React.ReactNode } }) => {
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <div
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => setShowDetails(false)}
      style={{
        padding: '12px 16px',
        border: '1px solid #9ca3af',
        borderRadius: '8px',
        background: '#f3f4f6',
        color: '#374151',
        textAlign: 'center',
        position: 'relative',
        boxShadow: showDetails ? '0 4px 12px rgba(0,0,0,0.15)' : '0 1px 3px rgba(0,0,0,0.1)',
        minWidth: 100,
        fontSize: 14,
        fontWeight: 500,
        cursor: 'grab',
      }}
    >
      {/* 4 invisible handles so the graph is connectable if you enable it later */}
      <Handle type="target" position={Position.Top} style={{ opacity: 0, width: 8, height: 8 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0, width: 8, height: 8 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0, width: 8, height: 8 }} />
      <Handle type="target" position={Position.Left} style={{ opacity: 0, width: 8, height: 8 }} />

      <div>{data.label}</div>

      {showDetails && (
        <div
          style={{
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            marginBottom: 10,
            padding: '12px 16px',
            borderRadius: 8,
            background: '#111827',
            color: '#f9fafb',
            fontSize: 13,
            maxWidth: 300,
            whiteSpace: 'normal',
            zIndex: 1000,
            boxShadow: '0 8px 16px rgba(0,0,0,0.2)',
            border: '1px solid #374151',
          }}
        >
          {/* put whatever text/joke you want here */}
          Edge hover tooltips are on the connections.
        </div>
      )}
    </div>
  );
};

/* ------------------------ Floating Straight Edge ---------------------------- */
/* Picks the closest point on each node, then draws a straight line between.   */

function getNodeCenter(node: any) {
  return { x: node.positionAbsolute.x + node.width / 2, y: node.positionAbsolute.y + node.height / 2 };
}

function getIntersectionPoint(sourceNode: any, targetNode: any) {
  // Rect-line intersection: from source center toward target center
  const src = getNodeCenter(sourceNode);
  const tgt = getNodeCenter(targetNode);

  const dx = tgt.x - src.x;
  const dy = tgt.y - src.y;

  const w = sourceNode.width / 2;
  const h = sourceNode.height / 2;

  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);

  // Decide which side we hit first
  let x = 0,
    y = 0;
  if (absDx / w > absDy / h) {
    // hit left/right
    x = src.x + (dx > 0 ? w : -w);
    y = src.y + (dy * (w / absDx));
  } else {
    // hit top/bottom
    y = src.y + (dy > 0 ? h : -h);
    x = src.x + (dx * (h / absDy));
  }

  return { x, y };
}

function getEdgeParams(sourceNode: any, targetNode: any) {
  const srcPoint = getIntersectionPoint(sourceNode, targetNode);
  const tgtPoint = getIntersectionPoint(targetNode, sourceNode);
  return { sx: srcPoint.x, sy: srcPoint.y, tx: tgtPoint.x, ty: tgtPoint.y };
}

const FloatingStraightEdge = (props: EdgeProps) => {
  const { source, target, id, data } = props;
  const { getNodes } = useReactFlow();
  const nodes = getNodes();

  const sourceNode = nodes.find((n) => n.id === source);
  const targetNode = nodes.find((n) => n.id === target);
  if (!sourceNode || !targetNode) return null;

  const { sx, sy, tx, ty } = getEdgeParams(sourceNode, targetNode);
  const [edgePath, labelX, labelY] = getStraightPath({
    sourceX: sx,
    sourceY: sy,
    targetX: tx,
    targetY: ty,
  });

  const [hover, setHover] = useState(false);
  const label = (data as any)?.tooltip ?? `${source} ↔ ${target}`;

  return (
    <>
      {/* fat invisible path to make hover easy */}
      <path
        d={edgePath}
        fill="none"
        stroke="transparent"
        strokeWidth={18}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        style={{ pointerEvents: 'all' }}
      />
      {/* visible edge */}
      <path d={edgePath} fill="none" stroke={hover ? '#111827' : '#6b7280'} strokeWidth={hover ? 4 : 3} />

      {/* tooltip */}
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: 'none',
            opacity: hover ? 1 : 0,
            transition: 'opacity 120ms ease',
            background: '#111827',
            color: '#f9fafb',
            padding: '6px 8px',
            borderRadius: 6,
            fontSize: 12,
            border: '1px solid #374151',
            boxShadow: '0 6px 14px rgba(0,0,0,0.25)',
            whiteSpace: 'nowrap',
            zIndex: 1000,
          }}
        >
          {label}
        </div>
      </EdgeLabelRenderer>
    </>
  );
};

const edgeTypes: EdgeTypes = { floating: FloatingStraightEdge };

/* --------------------------------- Data ------------------------------------- */

const initialNodes: Node[] = [
  { id: 'market', position: { x: 300, y: 50 }, data: { label: 'Market Trends' }, type: 'custom', draggable: true },
  { id: 'tech', position: { x: 150, y: 150 }, data: { label: 'Technology' }, type: 'custom', draggable: true },
  { id: 'finance', position: { x: 450, y: 150 }, data: { label: 'Finance' }, type: 'custom', draggable: true },
  { id: 'ai', position: { x: 100, y: 250 }, data: { label: 'AI/ML' }, type: 'custom', draggable: true },
  { id: 'cloud', position: { x: 200, y: 250 }, data: { label: 'Cloud Services' }, type: 'custom', draggable: true },
  { id: 'banking', position: { x: 400, y: 250 }, data: { label: 'Banking' }, type: 'custom', draggable: true },
  { id: 'crypto', position: { x: 500, y: 250 }, data: { label: 'Cryptocurrency' }, type: 'custom', draggable: true },
  { id: 'regulations', position: { x: 300, y: 350 }, data: { label: 'Regulations' }, type: 'custom', draggable: true },
];

const initialEdges: Edge[] = [
  { id: 'market-tech', source: 'market', target: 'tech', type: 'floating', data: { tooltip: 'Tech follows market signals' } },
  { id: 'market-finance', source: 'market', target: 'finance', type: 'floating', data: { tooltip: 'Macro → pricing & risk' } },
  { id: 'tech-ai', source: 'tech', target: 'ai', type: 'floating', data: { tooltip: 'AI is a subset of Tech' } },
  { id: 'tech-cloud', source: 'tech', target: 'cloud', type: 'floating', data: { tooltip: 'Cloud infra enables scale' } },
  { id: 'finance-banking', source: 'finance', target: 'banking', type: 'floating', data: { tooltip: 'Banking vertical' } },
  { id: 'finance-crypto', source: 'finance', target: 'crypto', type: 'floating', data: { tooltip: 'Digital assets' } },
  { id: 'ai-regulations', source: 'ai', target: 'regulations', type: 'floating', data: { tooltip: 'AI compliance' } },
  { id: 'crypto-regulations', source: 'crypto', target: 'regulations', type: 'floating', data: { tooltip: 'KYC/AML' } },
  { id: 'banking-regulations', source: 'banking', target: 'regulations', type: 'floating', data: { tooltip: 'Basel, PSD2…' } },
];

/* --------------------------------- Graph ------------------------------------ */

function GraphViz() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);
  const [showMiniMap, setShowMiniMap] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleMoveStart = useCallback(() => {
    setShowMiniMap(true);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
  }, []);

  const handleMoveEnd = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => setShowMiniMap(false), 2000);
  }, []);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onMoveStart={handleMoveStart}
        onMoveEnd={handleMoveEnd}
        fitView
        nodeTypes={{ custom: CustomNode }}
        edgeTypes={edgeTypes}
        defaultEdgeOptions={{ type: 'floating' }}
        edgesUpdatable={false}
        nodesConnectable={false}
        nodesDraggable
        panOnDrag
        zoomOnScroll
        panOnScroll={false}
      >
        <Controls />
        <MiniMap style={{ opacity: showMiniMap ? 1 : 0, transition: 'opacity 0.3s' }} />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}

export default GraphViz;
