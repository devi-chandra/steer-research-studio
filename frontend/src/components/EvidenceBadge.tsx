import React from 'react';

interface Props {
  status: string;
  type?: 'evidence' | 'review';
}

export const EvidenceBadge: React.FC<Props> = ({ status, type = 'evidence' }) => {
  let bg = 'bg-[#F5EBDF]';
  let text = 'text-[#351D1D]';
  let border = 'border-[#B58777]';
  let dot = 'bg-[#B58777]';

  if (type === 'evidence') {
    switch (status) {
      case 'Directly supported':
        bg = 'bg-emerald-50';
        text = 'text-emerald-800';
        border = 'border-emerald-300';
        dot = 'bg-emerald-600';
        break;
      case 'Partially supported':
        bg = 'bg-amber-50';
        text = 'text-amber-800';
        border = 'border-amber-300';
        dot = 'bg-amber-500';
        break;
      case 'Unsupported':
        bg = 'bg-rose-50';
        text = 'text-rose-800';
        border = 'border-rose-300';
        dot = 'bg-rose-600';
        break;
      case 'Unable to verify':
      default:
        bg = 'bg-stone-100';
        text = 'text-stone-700';
        border = 'border-stone-300';
        dot = 'bg-stone-400';
        break;
    }
  } else {
    // Review status
    switch (status) {
      case 'Approved':
        bg = 'bg-emerald-50';
        text = 'text-emerald-900';
        border = 'border-emerald-300';
        dot = 'bg-emerald-600';
        break;
      case 'Approved (Edited by Doctor)':
        bg = 'bg-blue-50';
        text = 'text-blue-900';
        border = 'border-blue-300';
        dot = 'bg-blue-600';
        break;
      case 'Changes Requested':
        bg = 'bg-amber-50';
        text = 'text-amber-900';
        border = 'border-amber-300';
        dot = 'bg-amber-600';
        break;
      case 'Rejected':
        bg = 'bg-rose-50';
        text = 'text-rose-900';
        border = 'border-rose-300';
        dot = 'bg-rose-600';
        break;
      case 'Pending Review':
      default:
        bg = 'bg-[#E6CBBD]/40';
        text = 'text-[#661414]';
        border = 'border-[#B58777]';
        dot = 'bg-[#C04E2A]';
        break;
    }
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${bg} ${text} ${border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      {status}
    </span>
  );
};
