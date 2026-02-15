import React from 'react'

/*
 * ATUM DESK Design System - Table Component
 */

export function Table({ 
  columns = [],
  data = [],
  onRowClick,
  emptyMessage = "No data available",
  loading = false,
  className = ''
}) {
  return (
    <div className={`overflow-x-auto rounded-lg border border-[var(--atum-border)] ${className}`}>
      <table className="w-full">
        <thead>
          <tr className="bg-[var(--atum-bg-2)] border-b border-[var(--atum-border)]">
            {columns.map((col, idx) => (
              <th 
                key={idx}
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[var(--atum-text-muted)]"
                style={{ width: col.width }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--atum-border)]">
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center">
                <div className="flex justify-center">
                  <div className="animate-spin h-6 w-6 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full"></div>
                </div>
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-[var(--atum-text-muted)]">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIdx) => (
              <tr 
                key={rowIdx}
                onClick={() => onRowClick && onRowClick(row)}
                className={`hover:bg-[var(--atum-bg-2)] transition-colors ${onRowClick ? 'cursor-pointer' : ''}`}
              >
                {columns.map((col, colIdx) => (
                  <td key={colIdx} className="px-4 py-3 text-sm text-[var(--atum-text-1)]">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export function TablePagination({ 
  page = 1,
  totalPages = 1,
  onPageChange,
  className = ''
}) {
  return (
    <div className={`flex items-center justify-between px-4 py-3 border-t border-[var(--atum-border)] ${className}`}>
      <div className="text-sm text-[var(--atum-text-muted)]">
        Page {page} of {totalPages}
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onPageChange && onPageChange(page - 1)}
          disabled={page <= 1}
          className="px-3 py-1 text-xs bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded hover:border-[var(--atum-accent-gold)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange && onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="px-3 py-1 text-xs bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded hover:border-[var(--atum-accent-gold)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  )
}

export default Table
