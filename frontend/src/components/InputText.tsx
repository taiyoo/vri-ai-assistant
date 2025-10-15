import React, { HTMLInputTypeAttribute, KeyboardEvent, ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

type Props = {
  className?: string;
  label?: string;
  type?: HTMLInputTypeAttribute;
  value: string;
  disabled?: boolean;
  placeholder?: string;
  hint?: string;
  errorMessage?: string;
  icon?: ReactNode;
  onChange?: (s: string) => void;
  onKeyDown?: (e: KeyboardEvent<HTMLInputElement>) => void;
};

const InputText = React.forwardRef<HTMLInputElement, Props>((props, ref) => {
  return (
    <div className={twMerge('flex flex-col', props.className)}>
      {props.icon && (
        <div className="relative inline-block">
          <div className="absolute left-2 top-2 text-lg">{props.icon}</div>
        </div>
      )}
      <input
        ref={ref}
        type={props.type ?? 'text'}
        className={twMerge(
          'peer h-9 rounded-md border p-2 transition-colors duration-200 bg-white dark:bg-ai4-dark-800',
          'text-ai4-gray-900 dark:text-ai4-gray-100 placeholder:text-ai4-gray-400 dark:placeholder:text-ai4-gray-500',
          'focus:outline-none focus:ring-2 focus:ring-ai4-blue-500 dark:focus:ring-ai4-blue-400 focus:border-transparent',
          props.errorMessage
            ? 'border-2 border-red-500'
            : 'border-ai4-gray-300 dark:border-ai4-dark-600 hover:border-ai4-gray-400 dark:hover:border-ai4-dark-500',
          props.icon ? 'pl-8' : ''
        )}
        disabled={props.disabled}
        value={props.value}
        placeholder={props.placeholder}
        onChange={(e) => {
          props.onChange ? props.onChange(e.target.value) : null;
        }}
        onKeyDown={props.onKeyDown}
      />

      {props.label && (
        <div
          className={twMerge(
            'order-first text-sm font-medium text-ai4-gray-700 dark:text-ai4-gray-300 peer-focus:text-ai4-blue-600 dark:peer-focus:text-ai4-blue-400',
            props.errorMessage
              ? 'text-red-600'
              : 'peer-focus:font-semibold'
          )}>
          {props.label}
        </div>
      )}
      {props.hint && !props.errorMessage && (
        <div className="mt-0.5 text-xs text-ai4-gray-500 dark:text-ai4-gray-400">
          {props.hint}
        </div>
      )}
      {props.errorMessage && (
        <div className="mt-0.5 text-xs text-red-600">{props.errorMessage}</div>
      )}
    </div>
  );
});

InputText.displayName = 'InputText';

export default InputText;
