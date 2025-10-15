import React, { ReactNode } from 'react';
import Help from '../components/Help';
import { TooltipDirection } from '../constants';
import Skeleton from '../components/Skeleton';

type Props = {
  pageTitle: string;
  pageTitleHelp?: string;
  pageTitleActions?: ReactNode;
  searchCondition?: ReactNode;
  isLoading?: boolean;
  isEmpty?: boolean;
  emptyMessage?: string;
  children: ReactNode;
};

const ListPageLayout: React.FC<Props> = (props) => {
  return (
    <div className="flex h-full justify-center">
      <div className="w-full max-w-screen-xl px-4 lg:w-4/5">
        <div className="size-full pt-8">
          <div className="flex justify-between">
            <div className="flex items-center gap-2">
              <div className="text-xl font-bold">{props.pageTitle}</div>
              {props.pageTitleHelp && (
                <Help
                  direction={TooltipDirection.RIGHT}
                  message={props.pageTitleHelp}
                />
              )}
            </div>
            {props.pageTitleActions && <div>{props.pageTitleActions}</div>}
          </div>
          {props.searchCondition && (
            <div className="my-2">{props.searchCondition}</div>
          )}
          <div className="mt-2 border-b border-ai4-gray-200 dark:border-ai4-dark-700"></div>

          <div className="-mr-2 h-[calc(100%-3rem)] overflow-x-auto overflow-y-scroll border-ai4-gray-200 dark:border-ai4-dark-700 scrollbar-thin scrollbar-thumb-ai4-gray-300 dark:scrollbar-thumb-ai4-dark-600">
            <div className="mr-2 h-full pb-8">
              {props.isLoading && (
                <div className="mt-2 flex flex-col gap-2">
                  {new Array(8).fill('').map((_, idx) => (
                    <Skeleton key={idx} className="h-12 w-full" />
                  ))}
                </div>
              )}
              {!props.isLoading && props.isEmpty && (
                <div className="flex size-full items-center justify-center italic text-ai4-gray-500 dark:text-ai4-gray-400">
                  {props.emptyMessage}
                </div>
              )}
              {!props.isLoading && !props.isEmpty && props.children}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListPageLayout;
