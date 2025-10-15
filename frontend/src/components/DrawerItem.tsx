import React, { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { twMerge } from 'tailwind-merge';

type Props = {
  className?: string;
  isActive?: boolean;
  isBlur?: boolean;
  to: string;
  icon: ReactNode;
  labelComponent: ReactNode;
  actionComponent?: ReactNode;
  onClick?: () => void;
};

const DrawerItem: React.FC<Props> = (props) => {
  return (
    <Link
      className={twMerge(
        'group mx-2 my-1 flex h-10 items-center rounded-lg px-2 transition-colors duration-200',
        (props.isActive ?? true)
          ? 'bg-ai4-blue-100 dark:bg-ai4-blue-900/30 text-ai4-blue-700 dark:text-ai4-blue-300'
          : 'text-ai4-gray-700 dark:text-ai4-gray-300 hover:bg-ai4-gray-50 dark:hover:bg-ai4-dark-800',
        props.className
      )}
      to={props.to}
      onClick={props.onClick}>
      <div className={`flex h-8 max-h-5 w-full justify-start overflow-hidden`}>
        <div className="mr-2 pt-0.5">{props.icon}</div>
        <div className="relative flex-1 text-ellipsis break-all">
          {props.labelComponent}
          {(props.isBlur ?? true) && (
            <div
              className={twMerge(
                'absolute inset-y-0 right-0 w-8 bg-gradient-to-l',
                props.isActive
                  ? 'from-ai4-blue-100 dark:from-ai4-blue-900/30'
                  : 'from-white dark:from-ai4-dark-900 group-hover:from-ai4-gray-50 dark:group-hover:from-ai4-dark-800'
              )}
            />
          )}
        </div>

        <div className="flex">{props.actionComponent}</div>
      </div>
    </Link>
  );
};

export default DrawerItem;
