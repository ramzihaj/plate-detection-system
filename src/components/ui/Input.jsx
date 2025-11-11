export const Input = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  error,
  disabled = false,
  required = false,
  className = '',
  icon: Icon
}) => {
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="h-5 w-5 text-gray-400" />
          </div>
        )}
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          className={`
            block w-full rounded-lg border border-gray-300 dark:border-gray-600 
            bg-white dark:bg-gray-700 
            text-gray-900 dark:text-white 
            placeholder-gray-400 dark:placeholder-gray-500
            focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed
            ${Icon ? 'pl-10' : 'pl-4'} pr-4 py-2
            ${error ? 'border-red-500 focus:ring-red-500' : ''}
          `}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
};

export const Textarea = ({
  label,
  value,
  onChange,
  placeholder,
  error,
  disabled = false,
  required = false,
  rows = 4,
  className = ''
}) => {
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        rows={rows}
        className={`
          block w-full rounded-lg border border-gray-300 dark:border-gray-600 
          bg-white dark:bg-gray-700 
          text-gray-900 dark:text-white 
          placeholder-gray-400 dark:placeholder-gray-500
          focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed
          px-4 py-2
          ${error ? 'border-red-500 focus:ring-red-500' : ''}
        `}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
};
