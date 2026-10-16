import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = 'max-w-lg'
}) => {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      if (!dialog.open) {
        dialog.showModal();
      }
    } else {
      if (dialog.open) {
        dialog.close();
      }
    }
  }, [isOpen]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    const handleCancel = (e: Event) => {
      e.preventDefault();
      onClose();
    };

    dialog.addEventListener('cancel', handleCancel);
    return () => dialog.removeEventListener('cancel', handleCancel);
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <dialog
      ref={dialogRef}
      className={`fixed inset-0 z-50 bg-[#121214] text-zinc-100 border border-[#27272a] rounded-lg shadow-2xl p-0 w-full ${maxWidth} backdrop:bg-black/75 backdrop:backdrop-blur-xs`}
    >
      <div className="flex items-center justify-between border-b border-[#27272a] px-5 py-4">
        <h3 className="text-sm font-semibold tracking-wide text-zinc-100">{title}</h3>
        <button
          onClick={onClose}
          type="button"
          className="text-zinc-400 hover:text-white transition-colors p-1 rounded hover:bg-zinc-800"
          aria-label="Close modal"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="p-5">{children}</div>
    </dialog>
  );
};
