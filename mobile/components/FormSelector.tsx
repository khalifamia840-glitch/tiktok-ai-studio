import { Picker } from '@react-native-picker/picker'
import { Platform, StyleSheet, Text, View } from 'react-native'
import { COLORS } from '../lib/constants'

interface FormSelectorProps {
  label: string
  value: string
  options: Array<{ value: string; label: string }>
  onChange: (value: string) => void
}

export default function FormSelector({
  label,
  value,
  options,
  onChange,
}: FormSelectorProps) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={value}
          onValueChange={(v) => onChange(String(v))}
          style={styles.picker}
          dropdownIconColor={COLORS.textSecondary}
          itemStyle={Platform.OS === 'ios' ? styles.iosItem : undefined}
        >
          {options.map((opt) => (
            <Picker.Item
              key={opt.value}
              label={opt.label}
              value={opt.value}
              color={Platform.OS === 'android' ? COLORS.textPrimary : undefined}
            />
          ))}
        </Picker>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  wrapper: {
    gap: 6,
  },
  label: {
    color: COLORS.textSecondary,
    fontSize: 13,
    fontWeight: '500',
  },
  pickerContainer: {
    backgroundColor: COLORS.cardBg,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    overflow: 'hidden',
  },
  picker: {
    color: COLORS.textPrimary,
    backgroundColor: 'transparent',
  },
  iosItem: {
    color: COLORS.textPrimary,
    backgroundColor: COLORS.cardBg,
  },
})
