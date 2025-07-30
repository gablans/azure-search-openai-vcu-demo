import React from "react";
import { Stack, Text, Link } from "@fluentui/react";
import { Play24Regular } from "@fluentui/react-icons";
import { StructuredVideoResponse, VideoSceneReference } from "../../api/models";
import styles from "./StructuredAnswerParser.module.css";

interface Props {
    structuredResponse: StructuredVideoResponse;
    onTimestampClick: (videoFile: string, timestamp: string) => void;
}

// Convert timestamp from "HH:MM:SS.mmm" to seconds for video player
const timestampToSeconds = (timestamp: string): number => {
    try {
        const parts = timestamp.split(":");
        if (parts.length >= 3) {
            const hours = parseInt(parts[0]) || 0;
            const minutes = parseInt(parts[1]) || 0;
            const secondsAndMs = parseFloat(parts[2]) || 0;
            return hours * 3600 + minutes * 60 + secondsAndMs;
        }
        return 0;
    } catch (e) {
        console.error("Error parsing timestamp:", e);
        return 0;
    }
};

// Format timestamp for display (remove milliseconds for cleaner look)
const formatTimestampForDisplay = (timestamp: string): string => {
    try {
        const parts = timestamp.split(":");
        if (parts.length >= 3) {
            const hours = parts[0];
            const minutes = parts[1];
            const seconds = parts[2].split(".")[0]; // Remove milliseconds
            return `${hours}:${minutes}:${seconds}`;
        }
        return timestamp;
    } catch (e) {
        return timestamp;
    }
};

export const StructuredAnswerParser: React.FC<Props> = ({ structuredResponse, onTimestampClick }) => {
    const handleTimestampClick = (scene: VideoSceneReference) => {
        onTimestampClick(scene.video_file, scene.start_timestamp);
    };

    return (
        <Stack className={styles.structuredAnswer}>
            {/* Main Description */}
            <Stack.Item className={styles.descriptionSection}>
                <Text variant="medium" className={styles.description}>
                    {structuredResponse.description}
                </Text>
            </Stack.Item>

            {/* Scene References */}
            {structuredResponse.scene_references && structuredResponse.scene_references.length > 0 && (
                <Stack.Item className={styles.sceneReferencesSection}>
                    <Text variant="mediumPlus" className={styles.sectionTitle}>
                        Scene references:
                    </Text>
                    <Stack className={styles.sceneList}>
                        {structuredResponse.scene_references.map((scene, index) => (
                            <Stack.Item key={index} className={styles.sceneItem}>
                                <Stack horizontal verticalAlign="center" className={styles.sceneHeader}>
                                    <Link onClick={() => handleTimestampClick(scene)} className={styles.timestampLink}>
                                        <Stack horizontal verticalAlign="center" tokens={{ childrenGap: 4 }}>
                                            <Play24Regular className={styles.playIcon} />
                                            <Text variant="medium" className={styles.timestampText}>
                                                {formatTimestampForDisplay(scene.start_timestamp)} - {formatTimestampForDisplay(scene.end_timestamp)}
                                            </Text>
                                        </Stack>
                                    </Link>
                                </Stack>
                                <Text variant="small" className={styles.sceneDescription}>
                                    {scene.description}
                                </Text>
                            </Stack.Item>
                        ))}
                    </Stack>
                </Stack.Item>
            )}

            {/* Key Features */}
            {structuredResponse.key_features && structuredResponse.key_features.length > 0 && (
                <Stack.Item className={styles.featuresSection}>
                    <Text variant="medium" className={styles.sectionTitle}>
                        Key features:
                    </Text>
                    <Stack horizontal wrap tokens={{ childrenGap: 8 }}>
                        {structuredResponse.key_features.map((feature, index) => (
                            <Text key={index} variant="small" className={styles.featureTag}>
                                {feature}
                            </Text>
                        ))}
                    </Stack>
                </Stack.Item>
            )}

            {/* Brands Mentioned */}
            {structuredResponse.brands_mentioned && structuredResponse.brands_mentioned.length > 0 && (
                <Stack.Item className={styles.brandsSection}>
                    <Text variant="medium" className={styles.sectionTitle}>
                        Brands:
                    </Text>
                    <Stack horizontal wrap tokens={{ childrenGap: 8 }}>
                        {structuredResponse.brands_mentioned.map((brand, index) => (
                            <Text key={index} variant="small" className={styles.brandTag}>
                                {brand}
                            </Text>
                        ))}
                    </Stack>
                </Stack.Item>
            )}
        </Stack>
    );
};
