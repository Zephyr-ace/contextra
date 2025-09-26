'use client';

import React, { useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  MarkerType,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
} from 'reactflow';

import 'reactflow/dist/style.css';

const CustomNode = ({ data }: { data: { label: React.ReactNode; details?: string; danger?: boolean } }) => {
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <div
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => setShowDetails(false)}
      style={{
        padding: '10px',
        border: data.danger ? '1px solid red' : '1px solid #ddd',
        borderRadius: '5px',
        background: '#FFF',
        color: '#333',
        textAlign: 'center',
        position: 'relative',
        boxShadow: showDetails ? '0 4px 8px rgba(0,0,0,0.2)' : 'none',
        transition: 'box-shadow 0.2s ease-in-out',
      }}
    >
      <div>{data.label}</div>
      {showDetails && data.details && (
        <div
          style={{
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            marginBottom: '10px',
            padding: '5px 10px',
            borderRadius: '3px',
            background: '#333',
            color: '#FFF',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            zIndex: 1000,
          }}
        >
          {data.details}
        </div>
      )}
    </div>
  );
};

const initialNodes: Node[] = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'China-Taiwan Conflict', details: 'Ongoing geopolitical tensions with potential global impact' }, type: 'custom' },
  { id: '2', position: { x: 250, y: 0 }, data: { label: 'Taiwan', details: 'Key player in semiconductor manufacturing' }, type: 'custom' },
  { id: '3', position: { x: 500, y: 100 }, data: { label: 'TSMC', details: 'Taiwan Semiconductor Manufacturing Company - world\'s largest dedicated independent semiconductor foundry' }, type: 'custom' },
  { id: '4', position: { x: 250, y: 200 }, data: { label: 'China', details: 'Major consumer and producer of goods' }, type: 'custom' },
  { id: '5', position: { x: 50, y: 250 }, data: { label: 'Geopolitics', details: 'Study of how geography and economics influence politics' }, type: 'custom' },
  { id: '6', position: { x: 400, y: 400 }, data: { label: 'Products', details: 'Goods and services produced and consumed' }, type: 'custom' },
  { 
    id: '7', 
    position: { x: 650, y: 500 }, 
    data: { 
      label: (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          Apple Stock 
          <div style={{ marginLeft: '5px', height: '8px', width: '8px', borderRadius: '50%', background: 'red' }} />
        </div>
      ),
      details: 'Potential risk due to supply chain disruption from Taiwan conflict',
      danger: true
    }, 
    type: 'custom' 
  }, // Red border for danger, red dot inside
];

const edgeStyle = { stroke: '#6b7280', strokeWidth: 1.5 } as const;

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', label: 'impacts heavily negative', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e1-4', source: '1', target: '4', label: 'impacts', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e1-5', source: '1', target: '5', label: 'impacts strongly negative', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e2-3', source: '2', target: '3', label: 'semiconductor production', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e3-4', source: '3', target: '4', label: 'supplies', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e4-6', source: '4', target: '6', label: 'consumes', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e5-4', source: '5', target: '4', label: 'inputs', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e5-6', source: '5', target: '6', label: 'uncertainty', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e3-7', source: '3', target: '7', label: 'produces in', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
  { id: 'e6-7', source: '6', target: '7', label: '', style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' } },
];

function GraphViz() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        defaultEdgeOptions={{
          style: { stroke: '#6b7280', strokeWidth: 1.5 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#6b7280' },
        }}
        nodeTypes={{ custom: CustomNode }}
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}

export default GraphViz;
