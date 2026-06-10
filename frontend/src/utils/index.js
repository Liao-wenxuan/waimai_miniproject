/** 工具函数 — 从 vant 中转导出，便于统一管理 */
import { showToast as vantShowToast, showSuccessToast, showFailToast, showConfirmDialog, showDialog, showLoadingToast, closeToast } from 'vant'

/**
 * 显示 Toast 提示
 * @param {string} message - 提示消息
 * @param {string} type - 'text' | 'success' | 'fail'
 */
export function showToast(message, type = 'text') {
  if (type === 'success') {
    showSuccessToast(message)
  } else if (type === 'fail') {
    showFailToast(message)
  } else {
    vantShowToast(message)
  }
}

export {
  showSuccessToast,
  showFailToast,
  showConfirmDialog,
  showDialog,
  showLoadingToast,
  closeToast
}
