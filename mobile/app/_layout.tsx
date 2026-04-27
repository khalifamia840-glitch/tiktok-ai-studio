import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'
import { COLORS } from '../lib/constants'

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" backgroundColor={COLORS.background} />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: COLORS.background },
          animation: 'fade',
        }}
      />
    </>
  )
}
