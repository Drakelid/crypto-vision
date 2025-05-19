import { useState, useCallback } from 'react';

type ValidationRules<T> = {
  [K in keyof T]?: {
    required?: boolean;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    validator?: (value: T[K], values: T) => string | null;
    message?: string;
  };
};

type FormErrors<T> = Partial<Record<keyof T, string>>;

interface UseFormReturn<T> {
  values: T;
  errors: FormErrors<T>;
  isSubmitting: boolean;
  isValid: boolean;
  handleChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => void;
  handleBlur: (
    e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => void;
  handleSubmit: (e: React.FormEvent) => void;
  setFieldValue: <K extends keyof T>(field: K, value: T[K]) => void;
  setFieldTouched: <K extends keyof T>(
    field: K,
    isTouched?: boolean
  ) => void;
  setValues: (values: T) => void;
  resetForm: () => void;
}

export const useForm = <T extends Record<string, any>>(
  initialValues: T,
  onSubmit: (values: T) => Promise<void> | void,
  validationRules: ValidationRules<T> = {}
): UseFormReturn<T> => {
  const [values, setValues] = useState<T>({ ...initialValues });
  const [errors, setErrors] = useState<FormErrors<T>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validate a single field
  const validateField = useCallback(
    (field: keyof T, value: T[keyof T]): string | null => {
      const rules = validationRules[field];
      if (!rules) return null;

      // Check required
      if (rules.required && (value === '' || value === null || value === undefined)) {
        return rules.message || 'This field is required';
      }

      // Skip further validation if the field is empty (but not required)
      if (value === '' || value === null || value === undefined) {
        return null;
      }

      const valueStr = String(value);

      // Check min length
      if (rules.minLength !== undefined && valueStr.length < rules.minLength) {
        return rules.message || `Must be at least ${rules.minLength} characters`;
      }

      // Check max length
      if (rules.maxLength !== undefined && valueStr.length > rules.maxLength) {
        return rules.message || `Must be at most ${rules.maxLength} characters`;
      }

      // Check pattern
      if (rules.pattern && !rules.pattern.test(valueStr)) {
        return rules.message || 'Invalid format';
      }

      // Custom validator
      if (rules.validator) {
        return rules.validator(value, values);
      }

      return null;
    },
    [validationRules, values]
  );

  // Validate all fields
  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors<T> = {};
    let isValid = true;

    Object.keys(values).forEach((key) => {
      const field = key as keyof T;
      const error = validateField(field, values[field]);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [values, validateField]);

  // Handle form submission
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      
      // Mark all fields as touched
      const newTouched: Partial<Record<keyof T, boolean>> = {};
      Object.keys(values).forEach((key) => {
        newTouched[key as keyof T] = true;
      });
      setTouched(newTouched);

      // Validate form
      const isValid = validateForm();
      if (!isValid) return;

      // Submit form
      setIsSubmitting(true);
      try {
        await onSubmit(values);
      } catch (error) {
        console.error('Form submission error:', error);
        // Handle form submission error (e.g., show error message)
      } finally {
        setIsSubmitting(false);
      }
    },
    [onSubmit, validateForm, values]
  );

  // Handle input change
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;
      const field = name as keyof T;

      // Handle different input types
      let parsedValue: any = value;
      if (type === 'number') {
        parsedValue = value === '' ? '' : parseFloat(value);
      } else if (type === 'checkbox') {
        parsedValue = (e.target as HTMLInputElement).checked;
      }

      // Update field value
      setValues((prev) => ({
        ...prev,
        [field]: parsedValue,
      }));

      // Validate field if it's been touched before
      if (touched[field]) {
        const error = validateField(field, parsedValue);
        setErrors((prev) => ({
          ...prev,
          [field]: error || undefined,
        }));
      }
    },
    [touched, validateField]
  );

  // Handle input blur
  const handleBlur = useCallback(
    (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name } = e.target;
      const field = name as keyof T;

      // Mark field as touched
      if (!touched[field]) {
        setTouched((prev) => ({
          ...prev,
          [field]: true,
        }));
      }

      // Validate field
      const error = validateField(field, values[field]);
      setErrors((prev) => ({
        ...prev,
        [field]: error || undefined,
      }));
    },
    [touched, validateField, values]
  );

  // Set field value programmatically
  const setFieldValue = useCallback(
    <K extends keyof T>(field: K, value: T[K]) => {
      setValues((prev) => ({
        ...prev,
        [field]: value,
      }));

      // Validate field if it's been touched before
      if (touched[field]) {
        const error = validateField(field, value);
        setErrors((prev) => ({
          ...prev,
          [field]: error || undefined,
        }));
      }
    },
    [touched, validateField]
  );

  // Set field touched state
  const setFieldTouched = useCallback(
    <K extends keyof T>(field: K, isTouched: boolean = true) => {
      if (touched[field] !== isTouched) {
        setTouched((prev) => ({
          ...prev,
          [field]: isTouched,
        }));

        // Validate field when it's marked as touched
        if (isTouched) {
          const error = validateField(field, values[field]);
          setErrors((prev) => ({
            ...prev,
            [field]: error || undefined,
          }));
        }
      }
    },
    [touched, validateField, values]
  );

  // Reset form to initial values
  const resetForm = useCallback(() => {
    setValues({ ...initialValues });
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  // Check if form is valid
  const isValid = Object.keys(errors).length === 0;

  return {
    values,
    errors,
    isSubmitting,
    isValid,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldTouched,
    setValues,
    resetForm,
  };
};

// Helper hook for field-level validation
export const useFieldValidation = <T extends Record<string, any>>(
  field: keyof T,
  form: UseFormReturn<T>
) => {
  const { errors, touched, setFieldTouched } = form;
  
  return {
    error: errors[field],
    touched: !!touched[field],
    onBlur: () => setFieldTouched(field, true),
  };
};
