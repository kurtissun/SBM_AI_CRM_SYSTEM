import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react'

export type AlertType = 'info' | 'success' | 'warning' | 'error'

interface AlertModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  message: string
  type?: AlertType
  confirmText?: string
  cancelText?: string
  onConfirm?: () => void
  showCancel?: boolean
}

export const AlertModal: React.FC<AlertModalProps> = ({
  isOpen,
  onClose,
  title,
  message,
  type = 'info',
  confirmText = 'OK',
  cancelText = 'Cancel',
  onConfirm,
  showCancel = false
}) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-12 h-12 text-green-600" />
      case 'warning':
        return <AlertTriangle className="w-12 h-12 text-yellow-600" />
      case 'error':
        return <AlertCircle className="w-12 h-12 text-red-600" />
      default:
        return <Info className="w-12 h-12 text-blue-600" />
    }
  }

  const getColorClasses = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          primary: 'bg-green-600 hover:bg-green-700',
          secondary: 'text-green-700 hover:bg-green-100'
        }
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          primary: 'bg-yellow-600 hover:bg-yellow-700',
          secondary: 'text-yellow-700 hover:bg-yellow-100'
        }
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          primary: 'bg-red-600 hover:bg-red-700',
          secondary: 'text-red-700 hover:bg-red-100'
        }
      default:
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          primary: 'bg-blue-600 hover:bg-blue-700',
          secondary: 'text-blue-700 hover:bg-blue-100'
        }
    }
  }

  const colors = getColorClasses()

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm()
    }
    onClose()
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', duration: 0.3 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md"
          >
            <div className="bg-white rounded-xl shadow-2xl overflow-hidden">
              {/* Header */}
              <div className={`${colors.bg} ${colors.border} border-b px-6 py-4`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getIcon()}
                    <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-1 hover:bg-white/50 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="px-6 py-4">
                <p className="text-gray-700 whitespace-pre-wrap">{message}</p>
              </div>

              {/* Actions */}
              <div className="px-6 py-4 bg-gray-50 flex items-center justify-end space-x-3">
                {showCancel && (
                  <button
                    onClick={onClose}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${colors.secondary}`}
                  >
                    {cancelText}
                  </button>
                )}
                <button
                  onClick={handleConfirm}
                  className={`px-4 py-2 rounded-lg font-medium text-white transition-colors ${colors.primary}`}
                >
                  {confirmText}
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Custom hook for managing alert modals
export const useAlertModal = () => {
  const [modalState, setModalState] = React.useState<{
    isOpen: boolean
    title: string
    message: string
    type: AlertType
    onConfirm?: () => void
    showCancel?: boolean
  }>({
    isOpen: false,
    title: '',
    message: '',
    type: 'info',
    showCancel: false
  })

  const showAlert = (
    title: string,
    message: string,
    type: AlertType = 'info',
    options?: {
      onConfirm?: () => void
      showCancel?: boolean
    }
  ) => {
    setModalState({
      isOpen: true,
      title,
      message,
      type,
      onConfirm: options?.onConfirm,
      showCancel: options?.showCancel
    })
  }

  const closeAlert = () => {
    setModalState(prev => ({ ...prev, isOpen: false }))
  }

  return {
    modalState,
    showAlert,
    closeAlert
  }
}