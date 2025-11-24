import React from 'react';

interface ResultBoxProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

const ResultBox: React.FC<ResultBoxProps> = ({ title, children, className = '' }) => {
  return (
    <div className={`result-box ${className}`}>
      <h3 className="box-title">{title}</h3>
      {children}
    </div>
  );
};

export default ResultBox;