# ==============================================================================
# NeverSMP — High-Performance Minecraft Java 21 Runtime
# Optimized with Eclipse Temurin, Jemalloc, and Aikar's GC Flags
# ==============================================================================

FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache bash curl tzdata jq libstdc++

# Set Timezone to Europe/Moscow
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /server

COPY entrypoint-mc.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Minecraft server standard port
EXPOSE 25565 25575

ENTRYPOINT ["/entrypoint.sh"]
