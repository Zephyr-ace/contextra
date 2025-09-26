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
  const { source, target, id, data, style } = props;
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

  // Get custom colors from style prop, fallback to default
  const defaultColor = '#6b7280';
  const hoverColor = '#111827';
  const edgeColor = (style?.stroke as string) || defaultColor;
  const edgeWidth = (style?.strokeWidth as number) || 3;

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
      <path 
        d={edgePath} 
        fill="none" 
        stroke={hover ? hoverColor : edgeColor} 
        strokeWidth={hover ? edgeWidth + 1 : edgeWidth} 
      />

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

/*
 * ========================================================================
 *                    HOW TO CREATE GRAPHS FROM BACKEND
 * ========================================================================
 * 
 * This component expects two arrays: `nodes` and `edges` following ReactFlow's
 * data structure. Here's exactly what you need to send from your backend:
 * 
 * 1. NODES ARRAY STRUCTURE:
 * -------------------------
 * Each node must be an object with these required properties:
 * 
 * interface Node {
 *   id: string;              // Unique identifier (e.g., "market", "tech", "ai")
 *   position: {              // X,Y coordinates on canvas
 *     x: number;             // Horizontal position (0 = left edge)
 *     y: number;             // Vertical position (0 = top edge)
 *   };
 *   data: {                  // Custom data for the node
 *     label: string;         // Text displayed inside the node
 *   };
 *   type: string;            // Must be "custom" to use our CustomNode component
 *   draggable: boolean;      // true = user can drag this node around
 * }
 * 
 * Example nodes array from backend:
 * [
 *   { 
 *     id: "stock_aapl", 
 *     position: { x: 100, y: 50 }, 
 *     data: { label: "Apple Inc." }, 
 *     type: "custom", 
 *     draggable: true 
 *   },
 *   { 
 *     id: "sector_tech", 
 *     position: { x: 300, y: 150 }, 
 *     data: { label: "Technology" }, 
 *     type: "custom", 
 *     draggable: true 
 *   }
 * ]
 * 
 * 2. EDGES ARRAY STRUCTURE:
 * -------------------------
 * Each edge connects two nodes and must have these properties:
 * 
 * interface Edge {
 *   id: string;              // Unique identifier (e.g., "aapl-tech")
 *   source: string;          // ID of source node (must match a node.id)
 *   target: string;          // ID of target node (must match a node.id)
 *   type: string;            // Must be "floating" to use our custom edge
 *   data?: {                 // Optional custom data
 *     tooltip?: string;      // Text shown on hover (optional)
 *   };
 *   style?: {                // Optional styling
 *     stroke?: string;       // Color (hex code like "#ff0000" for red)
 *     strokeWidth?: number;  // Thickness (1-10, default is 3)
 *   };
 * }
 * 
 * Example edges array from backend:
 * [
 *   { 
 *     id: "aapl-tech", 
 *     source: "stock_aapl", 
 *     target: "sector_tech", 
 *     type: "floating",
 *     data: { tooltip: "Apple belongs to tech sector" },
 *     style: { stroke: "#10b981", strokeWidth: 4 }  // Green, thick line
 *   },
 *   { 
 *     id: "tech-market", 
 *     source: "sector_tech", 
 *     target: "market_trends", 
 *     type: "floating",
 *     data: { tooltip: "Tech follows market trends" }
 *     // No style = uses default gray color
 *   }
 * ]
 * 
 * 3. BACKEND JSON STRUCTURE:
 * --------------------------
 * Your backend should return JSON in this exact format:
 * 
 * {
 *   "nodes": [
 *     {
 *       "id": "node1",
 *       "position": { "x": 100, "y": 50 },
 *       "data": { "label": "Node 1" },
 *       "type": "custom",
 *       "draggable": true
 *     },
 *     {
 *       "id": "node2", 
 *       "position": { "x": 300, "y": 150 },
 *       "data": { "label": "Node 2" },
 *       "type": "custom",
 *       "draggable": true
 *     }
 *   ],
 *   "edges": [
 *     {
 *       "id": "edge1",
 *       "source": "node1",
 *       "target": "node2", 
 *       "type": "floating",
 *       "data": { "tooltip": "Connection info" },
 *       "style": { "stroke": "#ff0000", "strokeWidth": 4 }
 *     }
 *   ]
 * }
 * 
 * 4. COLORS FOR EDGES:
 * --------------------
 * Use these hex codes for different colors:
 * - Red: "#ef4444" or "#dc2626" (brighter)
 * - Green: "#10b981" 
 * - Blue: "#3b82f6"
 * - Purple: "#8b5cf6"
 * - Orange: "#f59e0b"
 * - Gray (default): "#6b7280"
 * 
 * 5. POSITIONING TIPS:
 * --------------------
 * - Canvas size is typically 800x600 pixels
 * - Keep x coordinates between 50-750 to avoid clipping
 * - Keep y coordinates between 50-550 to avoid clipping
 * - Space nodes at least 100-150 pixels apart for readability
 * - Use a grid layout (e.g., 200px spacing) for clean organization
 * 
 * 6. INTEGRATION EXAMPLE:
 * -----------------------
 * In your React component, replace the static data with API call:
 * 
 * const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
 * 
 * useEffect(() => {
 *   fetch('/api/graph-data')
 *     .then(res => res.json())
 *     .then(data => {
 *       setGraphData(data);
 *     });
 * }, []);
 * 
 * Then use: 
 * const [nodes, setNodes, onNodesChange] = useNodesState(graphData.nodes);
 * const [edges, setEdges, onEdgesChange] = useEdgesState(graphData.edges);
 * 
 * 7. DYNAMIC UPDATES:
 * -------------------
 * To update the graph after initial load:
 * - Call setNodes(newNodesArray) to update nodes
 * - Call setEdges(newEdgesArray) to update edges
 * - The graph will automatically re-render with new data
 * 
 * ========================================================================
 */

const initialNodes: Node[] = [
  { id: 'china-taiwan-conflict', position: { x: 100, y: 50 }, data: { label: 'China-Taiwan Conflict' }, type: 'custom', draggable: true },
  { id: 'taiwan', position: { x: 400, y: 100 }, data: { label: 'Taiwan' }, type: 'custom', draggable: true },
  { id: 'china', position: { x: 250, y: 200 }, data: { label: 'China' }, type: 'custom', draggable: true },
  { id: 'geopolitics', position: { x: 50, y: 300 }, data: { label: 'Geopolitics' }, type: 'custom', draggable: true },
  { id: 'tsmc', position: { x: 400, y: 250 }, data: { label: 'TSMC' }, type: 'custom', draggable: true },
  { id: 'products', position: { x: 250, y: 350 }, data: { label: 'Products' }, type: 'custom', draggable: true },
  { id: 'apple-stock', position: { x: 500, y: 400 }, data: { label: 'Apple Stock' }, type: 'custom', draggable: true },
];

const initialEdges: Edge[] = [
  // Red chain: China-Taiwan Conflict -> Taiwan -> TSMC -> Apple Stock
  { 
    id: 'conflict-taiwan', 
    source: 'china-taiwan-conflict', 
    target: 'taiwan', 
    type: 'floating', 
    data: { tooltip: 'impacts heavily negative' },
    style: { stroke: '#ef4444', strokeWidth: 4 } // Red
  },
  { 
    id: 'taiwan-tsmc', 
    source: 'taiwan', 
    target: 'tsmc', 
    type: 'floating', 
    data: { tooltip: 'Semiconductor production' },
    style: { stroke: '#ef4444', strokeWidth: 4 } // Red
  },
  { 
    id: 'tsmc-apple', 
    source: 'tsmc', 
    target: 'apple-stock', 
    type: 'floating', 
    data: { tooltip: 'supplies' },
    style: { stroke: '#ef4444', strokeWidth: 4 } // Red
  },
  
  // All other edges in neutral grey
  { 
    id: 'conflict-china', 
    source: 'china-taiwan-conflict', 
    target: 'china', 
    type: 'floating', 
    data: { tooltip: 'impacts' },
    style: { stroke: '#6b7280', strokeWidth: 3 } // Grey
  },
  { 
    id: 'conflict-geopolitics', 
    source: 'china-taiwan-conflict', 
    target: 'geopolitics', 
    type: 'floating', 
    data: { tooltip: 'impacts strongly negative' },
    style: { stroke: '#6b7280', strokeWidth: 3 } // Grey
  },
  { 
    id: 'china-products', 
    source: 'china', 
    target: 'products', 
    type: 'floating', 
    data: { tooltip: 'consumes' },
    style: { stroke: '#6b7280', strokeWidth: 3 } // Grey
  },
  { 
    id: 'china-apple', 
    source: 'china', 
    target: 'apple-stock', 
    type: 'floating', 
    data: { tooltip: 'produces in' },
    style: { stroke: '#6b7280', strokeWidth: 3 } // Grey
  },
  { 
    id: 'geopolitics-china', 
    source: 'geopolitics', 
    target: 'china', 
    type: 'floating', 
    data: { tooltip: 'inputs' },
    style: { stroke: '#6b7280', strokeWidth: 3 } // Grey
  },
  { 
    id: 'geopolitics-products', 
    source: 'geopolitics', 
    target: 'products', 
    type: 'floating', 
    data: { tooltip: 'uncertainty' },
    style: { stroke: '#6b7280', strokeWidth: 3 } // Grey
  },
  { 
    id: 'products-apple', 
    source: 'products', 
    target: 'apple-stock', 
    type: 'floating', 
    data: { tooltip: '' },
    style: { stroke: '#6b7280', strokeWidth: 3 } // Grey
  },
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
