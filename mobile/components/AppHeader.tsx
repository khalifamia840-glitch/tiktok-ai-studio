import { LinearGradient } from 'expo-linear-gradient'
import { StyleSheet, Text, View } from 'react-native'
import { COLORS } from '../lib/constants'

interface AppHeaderProps {
  title?: string
}

export default function AppHeader({ title }: AppHeaderProps) {
  return (
    <View style={styles.container}>
      <View style={styles.logoRow}>
        <LinearGradient
          colors={[COLORS.primary, COLORS.secondary]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.iconBadge}
        >
          <Text style={styles.iconText}>▶</Text>
        </LinearGradient>
        <Text style={styles.logoText}>
          <Text style={styles.logoTikTok}>TikTok</Text>
          <Text style={styles.logoAI}> AI</Text>
        </Text>
      </View>
      {title ? <Text style={styles.subtitle}>{title}</Text> : null}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: COLORS.background,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  iconBadge: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconText: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: 'bold',
  },
  logoText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  logoTikTok: {
    color: COLORS.textPrimary,
  },
  logoAI: {
    color: COLORS.primary,
  },
  subtitle: {
    color: COLORS.textSecondary,
    fontSize: 13,
    marginTop: 2,
  },
})
