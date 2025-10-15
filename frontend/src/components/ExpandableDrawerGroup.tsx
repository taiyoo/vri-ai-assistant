import React, { ReactNode, useState } from 'react';
import { PiCaretDown } from 'react-icons/pi';
import { twMerge } from 'tailwind-merge';

type Props = {
  className?: string;
  label: string;
  children: ReactNode;
  isDefaultShow?: boolean;
};

const ExpandableDrawerGroup: React.FC<Props> = ({
  isDefaultShow = true,
  ...props
}) => {
  const [isShow, setIsShow] = useState(isDefaultShow);

  return (
    <div className={twMerge(props.className)}>
      <div
        className="flex w-full cursor-pointer items-center transition-colors duration-200 text-ai4-gray-700 dark:text-ai4-gray-300 hover:text-ai4-blue-600 dark:hover:text-ai4-blue-400"
        onClick={() => {
          setIsShow(!isShow);
        }}>
        <PiCaretDown className={`mx-1 text-sm transition-transform duration-200 ${isShow ? '' : 'rotate-180'}`} />

        <div className="font-medium">{props.label}</div>
      </div>
      <div className="">
        <div
          className={`origin-top transition-all ${
            isShow ? 'visible' : 'h-0 scale-y-0'
          }`}>
          {props.children}
        </div>
      </div>
    </div>
  );
};

export default ExpandableDrawerGroup;
