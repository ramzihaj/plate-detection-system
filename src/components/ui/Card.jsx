export const Card = ({ children, className = '' }) => {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '' }) => {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  );
};

export const CardTitle = ({ children, className = '' }) => {
  return (
    <h3 className={`text-xl font-semibold text-gray-900 dark:text-white ${className}`}>
      {children}
    </h3>
  );
};

export const CardContent = ({ children, className = '' }) => {
  return (
    <div className={className}>
      {children}
    </div>
  );
};
