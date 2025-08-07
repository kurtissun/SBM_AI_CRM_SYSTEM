import React from 'react'
import { AlertModal } from '@/components/modals/AlertModal'
import { useAlertStore } from '@/lib/alertService'

export const AlertProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { alert, closeAlert } = useAlertStore()

  return (
    <>
      {children}
      <AlertModal
        isOpen={alert.isOpen}
        onClose={closeAlert}
        title={alert.title}
        message={alert.message}
        type={alert.type}
        onConfirm={alert.onConfirm}
        showCancel={alert.showCancel}
      />
    </>
  )
}