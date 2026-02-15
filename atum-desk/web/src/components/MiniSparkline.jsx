import React from 'react'

/**
 * MiniSparkline — lightweight SVG sparkline (no chart library needed).
 * 
 * Usage:
 *   <MiniSparkline data={[12, 45, 23, 67, 34, 89, 56]} color="#22c55e" />
 */
export default function MiniSparkline({
    data = [],
    width = 80,
    height = 24,
    color = 'var(--atum-accent-gold)',
    strokeWidth = 1.5,
    filled = true,
    className = ''
}) {
    if (data.length < 2) return null

    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1

    const points = data.map((val, i) => ({
        x: (i / (data.length - 1)) * width,
        y: height - ((val - min) / range) * (height - 4) - 2
    }))

    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')

    const fillD = `${pathD} L ${width} ${height} L 0 ${height} Z`

    return (
        <svg
            width={width}
            height={height}
            viewBox={`0 0 ${width} ${height}`}
            className={className}
            style={{ display: 'inline-block', verticalAlign: 'middle' }}
        >
            {filled && (
                <path
                    d={fillD}
                    fill={color}
                    fillOpacity={0.1}
                />
            )}
            <path
                d={pathD}
                fill="none"
                stroke={color}
                strokeWidth={strokeWidth}
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            {/* End dot */}
            <circle
                cx={points[points.length - 1].x}
                cy={points[points.length - 1].y}
                r={2}
                fill={color}
            />
        </svg>
    )
}
