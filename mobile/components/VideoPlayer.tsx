import { Video, ResizeMode } from 'expo-av'
import { StyleProp, StyleSheet, View, ViewStyle } from 'react-native'

interface VideoPlayerProps {
  uri: string
  style?: StyleProp<ViewStyle>
}

export default function VideoPlayer({ uri, style }: VideoPlayerProps) {
  return (
    <View style={[styles.container, style]}>
      <Video
        source={{ uri }}
        style={styles.video}
        useNativeControls
        resizeMode={ResizeMode.CONTAIN}
        shouldPlay={false}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#000000',
    aspectRatio: 9 / 16,
    width: '100%',
  },
  video: {
    flex: 1,
  },
})
