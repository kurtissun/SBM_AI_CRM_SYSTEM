import { create } from 'zustand'
import { AlertType } from '@/components/modals/AlertModal'

interface AlertState {
  isOpen: boolean
  title: string
  message: string
  type: AlertType
  onConfirm?: () => void
  showCancel?: boolean
}

interface AlertStore {
  alert: AlertState
  showAlert: (
    title: string,
    message: string,
    type?: AlertType,
    options?: {
      onConfirm?: () => void
      showCancel?: boolean
    }
  ) => void
  closeAlert: () => void
}

export const useAlertStore = create<AlertStore>((set) => ({
  alert: {
    isOpen: false,
    title: '',
    message: '',
    type: 'info',
    showCancel: false
  },
  showAlert: (title, message, type = 'info', options) => {
    set({
      alert: {
        isOpen: true,
        title,
        message,
        type,
        onConfirm: options?.onConfirm,
        showCancel: options?.showCancel || false
      }
    })
  },
  closeAlert: () => {
    set((state) => ({
      alert: {
        ...state.alert,
        isOpen: false
      }
    }))
  }
}))

// Global alert functions for easier usage
export const showAlert = (
  title: string,
  message: string,
  type: AlertType = 'info',
  options?: {
    onConfirm?: () => void
    showCancel?: boolean
  }
) => {
  useAlertStore.getState().showAlert(title, message, type, options)
}

export const closeAlert = () => {
  useAlertStore.getState().closeAlert()
}