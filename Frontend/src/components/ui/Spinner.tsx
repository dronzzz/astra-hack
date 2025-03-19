import React from "react";

interface SpinnerProps {
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({ className = "" }) => {
  return (
    <div
      className={`animate-spin rounded-full border-2 border-t-transparent ${className}`}
    ></div>
  );
};

export default Spinner;
