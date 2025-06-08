/* eslint-disable */
// @ts-ignore
import * as API from './types';

export function displayCardStatusEnum(field: API.ICardStatus) {
  return {
    active: 'active',
    inactive: 'inactive',
    frozen: 'frozen',
    cancelled: 'cancelled',
  }[field];
}

export function displayCardTypeEnum(field: API.ICardType) {
  return {
    visa: 'visa',
    mastercard: 'mastercard',
    unionpay: 'unionpay',
    amex: 'amex',
    jcb: 'jcb',
    discover: 'discover',
    diners: 'diners',
  }[field];
}

export function displayCodeTypeEnum(field: API.ICodeType) {
  return {
    login: 'login',
    register: 'register',
    reset_password: 'reset_password',
    bind_phone: 'bind_phone',
  }[field];
}

export function displayFeeTypeEnum(field: API.IFeeType) {
  return {
    rigid: 'rigid',
    transaction_count: 'transaction_count',
    points_exchange: 'points_exchange',
    transaction_amount: 'transaction_amount',
  }[field];
}

export function displayGenderEnum(field: API.IGender) {
  return { male: 'male', female: 'female', unknown: 'unknown' }[field];
}

export function displayRecommendationStatusEnum(
  field: API.IRecommendationStatus
) {
  return {
    active: 'active',
    expired: 'expired',
    applied: 'applied',
    rejected: 'rejected',
  }[field];
}

export function displayRecommendationTypeEnum(field: API.IRecommendationType) {
  return {
    cashback: 'cashback',
    points: 'points',
    travel: 'travel',
    dining: 'dining',
    shopping: 'shopping',
    fuel: 'fuel',
  }[field];
}

export function displayReminderStatusEnum(field: API.IReminderStatus) {
  return { pending: 'pending', sent: 'sent', read: 'read', ignored: 'ignored' }[
    field
  ];
}

export function displayReminderTypeEnum(field: API.IReminderType) {
  return {
    payment: 'payment',
    bill: 'bill',
    annual_fee: 'annual_fee',
    overdue: 'overdue',
  }[field];
}

export function displayWaiverStatusEnum(field: API.IWaiverStatus) {
  return {
    pending: 'pending',
    waived: 'waived',
    paid: 'paid',
    overdue: 'overdue',
  }[field];
}
