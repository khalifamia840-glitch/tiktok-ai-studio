import { Pressable, StyleSheet, Text, View } from 'react-native'
import { COLORS } from '../lib/constants'

interface ToggleGroupProps {
  options: Array<{ value: string | number; label: string }>
  value: string | number
  onChange: (value: string | number) => void
  activeColor?: string
  activeTextColor?: string
}

export default function ToggleGroup({
  options,
  value,
  onChange,
  activeColor = COLORS.primary,
  activeTextColor = COLORS.textPrimary,
}: ToggleGroupProps) {
  return (
    <View style={styles.row}>
      {options.map((opt) => {
        const isActive = opt.value === value
        return (
          <Pressable
            key={String(opt.value)}
            onPress={() => onChange(opt.value)}
            style={[
              styles.button,
              isActive
                ? { backgroundColor: activeColor }
                : styles.buttonInactive,
            ]}
          >
            <Text
              style={[
                styles.label,
                isActive
                  ? { color: activeTextColor }
                  : styles.labelInactive,
              ]}
            >
              {opt.label}
            </Text>
          </Pressable>
        )
      })}
    </View>
  )
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    gap: 8,
  },
  button: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonInactive: {
    backgroundColor: COLORS.cardBg,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
  },
  labelInactive: {
    color: COLORS.textSecondary,
  },
})
