import React, { forwardRef } from 'react';
import { BaseProps } from '../@types/common';
import { PiSpinnerGap } from 'react-icons/pi';
import { twMerge } from 'tailwind-merge';

type Props = BaseProps & {
  icon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  disabled?: boolean;
  text?: boolean;
  outlined?: boolean;
  loading?: boolean;
  onClick: () => void;
  children: React.ReactNode;
};

const Button = forwardRef<HTMLButtonElement, Props>((props, ref) => {
  return (
    <button
      ref={ref}
      className={twMerge(
        'flex items-center justify-center whitespace-nowrap rounded-lg border p-1 px-3 font-medium transition-all duration-200',
        props.text && 'border-0 text-ai4-blue-600 dark:text-ai4-blue-400 hover:text-ai4-blue-700 dark:hover:text-ai4-blue-300 hover:bg-ai4-blue-50 dark:hover:bg-ai4-blue-900/20',
        props.outlined && 'border-ai4-blue-200 dark:border-ai4-blue-700 text-ai4-blue-600 dark:text-ai4-blue-400 hover:bg-ai4-blue-50 dark:hover:bg-ai4-blue-900/20 hover:border-ai4-blue-300 dark:hover:border-ai4-blue-600 bg-white dark:bg-ai4-dark-800',
        !props.text &&
          !props.outlined &&
          'bg-ai4-blue-600 dark:bg-ai4-blue-500 border-ai4-blue-600 dark:border-ai4-blue-500 text-white hover:bg-ai4-blue-700 dark:hover:bg-ai4-blue-600 hover:border-ai4-blue-700 dark:hover:border-ai4-blue-600 shadow-sm',
        props.disabled || props.loading ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md',
        props.className
      )}
      onClick={(e) => {
        e.stopPropagation();
        e.preventDefault();
        props.onClick();
      }}
      disabled={props.disabled || props.loading}>
      {props.icon && !props.loading && (
        <div className="-ml-1 mr-2">{props.icon}</div>
      )}
      {props.loading && <PiSpinnerGap className="-ml-1 mr-2 animate-spin" />}
      {props.children}
      {props.rightIcon && <div className="ml-2">{props.rightIcon}</div>}
    </button>
  );
});

export default Button;
