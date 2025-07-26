import React, { useRef, useEffect, useState } from "react";
import { Stack, Text } from "@fluentui/react";
import styles from "./VideoPlayer.module.css";

interface Props {
    videoFileName: string;
    timestamp?: string;
    width?: string;
    height?: string;
}

export const VideoPlayer = ({ videoFileName, timestamp = "00:00:00", width = "100%", height = "400px" }: Props) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [videoSrc, setVideoSrc] = useState<string>("");
    const [error, setError] = useState<string>("");

    // Convert timestamp from "HH:MM:SS.mmm" to seconds
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

    useEffect(() => {
        // Construct the video URL
        const videoUrl = `/content_understanding/videos/${videoFileName}`;
        setVideoSrc(videoUrl);
    }, [videoFileName]);

    useEffect(() => {
        if (videoRef.current && videoSrc) {
            const video = videoRef.current;

            const handleLoadedData = () => {
                if (timestamp && timestamp !== "00:00:00") {
                    const seekTime = timestampToSeconds(timestamp);
                    video.currentTime = seekTime;
                }
            };

            const handleError = () => {
                setError(`Could not load video: ${videoFileName}`);
            };

            video.addEventListener("loadeddata", handleLoadedData);
            video.addEventListener("error", handleError);

            return () => {
                video.removeEventListener("loadeddata", handleLoadedData);
                video.removeEventListener("error", handleError);
            };
        }
    }, [videoSrc, timestamp]);

    if (error) {
        return (
            <Stack className={styles.errorContainer}>
                <Text variant="medium" className={styles.errorText}>
                    {error}
                </Text>
                <Text variant="small">Expected video path: /content_understanding/videos/{videoFileName}</Text>
            </Stack>
        );
    }

    return (
        <Stack className={styles.videoContainer}>
            <Stack.Item>
                <Text variant="medium" className={styles.videoTitle}>
                    Video: {videoFileName}
                    {timestamp && timestamp !== "00:00:00" && <span className={styles.timestampInfo}> - Seeking to {timestamp}</span>}
                </Text>
            </Stack.Item>
            <Stack.Item>
                <video ref={videoRef} src={videoSrc} controls width={width} height={height} className={styles.videoPlayer} preload="metadata">
                    Your browser does not support the video tag.
                </video>
            </Stack.Item>
        </Stack>
    );
};
