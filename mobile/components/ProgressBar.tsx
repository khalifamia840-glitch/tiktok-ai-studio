import { LinearGradient } from 'expo-linear-gradient'
import { StyleSheet, Text, View } from 'react-native'
import { COLORS } from '../lib/constants'

interface ProgressBarProps {
  progress: number // 0–100
  message: string
}

export default function ProgressBar({ progress, message }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, progress))

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.message}>{message}</Text>
        <Text style={styles.percent}>{clamped}%</Text>
      </View>
      <View style={styles.track}>
        <LinearGradient
          colors={[COLORS.primary, COLORS.secondary]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={[styles.fill, { width: `${clamped}%` }]}
        />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    gap: 6,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  message: {
    color: COLORS.textSecondary,
    fontSize: 13,
    flex: 1,
    marginRight: 8,
  },
  percent: {
    color: COLORS.textPrimary,
    fontSize: 13,
    fontWeight: '600',
  },
  track: {
    height: 6,
    backgroundColor: COLORS.border,
    borderRadius: 3,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    borderRadius: 3,
  },
})
