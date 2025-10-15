import React from 'react';
import { BaseProps } from '../@types/common';
import { twMerge } from 'tailwind-merge';

type Props = BaseProps & {
  disabled?: boolean;
  onClick: (e: React.MouseEvent) => void;
  children: React.ReactNode;
};

const ButtonIcon: React.FC<Props> = (props) => {
  return (
    <button
      className={twMerge(
        'flex items-center justify-center rounded-full p-2 text-xl transition-all duration-200',
        'text-ai4-gray-600 dark:text-ai4-gray-400 hover:text-ai4-blue-600 dark:hover:text-ai4-blue-400 hover:bg-ai4-blue-50 dark:hover:bg-ai4-blue-900/20',
        props.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md',
        props.className
      )}
      onClick={(e) => {
        e.stopPropagation();
        e.preventDefault();
        props.onClick(e);
      }}
      disabled={props.disabled}>
      {props.children}
    </button>
  );
};

export default ButtonIcon;
