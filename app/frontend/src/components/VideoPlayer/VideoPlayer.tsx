import React, { useRef, useEffect, useState, useImperativeHandle, forwardRef } from "react";
import { Stack, Text } from "@fluentui/react";
import styles from "./VideoPlayer.module.css";

interface Props {
    videoFileName: string;
    timestamp?: string;
    width?: string;
    height?: string;
}

export interface VideoPlayerRef {
    seekToTimestamp: (timestamp: string) => void;
}

export const VideoPlayer = forwardRef<VideoPlayerRef, Props>(({ videoFileName, timestamp = "00:00:00", width = "100%", height = "400px" }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [videoSrc, setVideoSrc] = useState<string>("");
    const [error, setError] = useState<string>("");
    const [currentTimestamp, setCurrentTimestamp] = useState<string>(timestamp);

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

    // Expose methods to parent component
    useImperativeHandle(ref, () => ({
        seekToTimestamp: (newTimestamp: string) => {
            setCurrentTimestamp(newTimestamp);
            if (videoRef.current && videoSrc) {
                const seekTime = timestampToSeconds(newTimestamp);
                videoRef.current.currentTime = seekTime;
                videoRef.current.play().catch(err => console.log("Video play failed:", err));
            }
        }
    }));

    useEffect(() => {
        // Construct the video URL
        const videoUrl = `/content_understanding/videos/${videoFileName}`;
        setVideoSrc(videoUrl);
    }, [videoFileName]);

    useEffect(() => {
        if (videoRef.current && videoSrc) {
            const video = videoRef.current;

            const handleLoadedData = () => {
                if (currentTimestamp && currentTimestamp !== "00:00:00") {
                    const seekTime = timestampToSeconds(currentTimestamp);
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
    }, [videoSrc, currentTimestamp]);

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
                    {currentTimestamp && currentTimestamp !== "00:00:00" && <span className={styles.timestampInfo}> - Seeking to {currentTimestamp}</span>}
                </Text>
            </Stack.Item>
            <Stack.Item>
                <video ref={videoRef} src={videoSrc} controls width={width} height={height} className={styles.videoPlayer} preload="metadata">
                    Your browser does not support the video tag.
                </video>
            </Stack.Item>
        </Stack>
    );
});
