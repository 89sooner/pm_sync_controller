#!/bin/bash

# 색상 및 스타일 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

# 구분선 정의
SEPARATOR="============================================================"

# 스크립트 실행 시작 시간 기록
echo -e "${BOLD}${BLUE}${SEPARATOR}${RESET}"
echo -e "${BOLD}${BLUE}=== Script started at $(date -u) ===${RESET}"
echo -e "${BOLD}${BLUE}=== User: $USER ===${RESET}"
echo -e "${BOLD}${BLUE}${SEPARATOR}${RESET}"

# 컨테이너, 볼륨, 이미지 정리 함수
cleanup() {
    echo -e "${YELLOW}${SEPARATOR}${RESET}"
    echo -e "${YELLOW}Cleaning up existing resources...${RESET}"
    
    # 실행 중인 특정 컨테이너 강제 중지 및 제거
    if [ "$(docker ps -aq --filter "name=fastapi-webhooks-app")" ]; then
        echo -e "${YELLOW}Stopping and removing specific containers...${RESET}"
        docker compose down --volumes --remove-orphans
        docker rm -f $(docker ps -aq --filter "name=fastapi-webhooks-app")
    fi

    # 잠시 대기하여 리소스가 완전히 해제되도록 함
    sleep 5

    # 미사용 볼륨 제거
    # if [ "$(docker volume ls -q -f dangling=true)" ]; then
    #     echo -e "${YELLOW}Removing unused volumes...${RESET}"
    #     docker volume rm -f $(docker volume ls -q -f dangling=true)
    # fi

    # 프로젝트 관련 볼륨 명시적 제거
    # echo -e "${YELLOW}Removing project volumes...${RESET}"
    # docker volume rm -f fastapi-webhooks-app_postgres_data 2>/dev/null || true

    # 태그가 none인 이미지 제거
    if [ "$(docker images -f "dangling=true" -q)" ]; then
        echo -e "${YELLOW}Removing dangling images...${RESET}"
        docker rmi -f $(docker images -f "dangling=true" -q)
    fi

    # 프로젝트 관련 이미지 제거
    if [ "$(docker images -q fastapi-webhooks-app-web)" ]; then
        # 이미지 사용 중인 컨테이너 강제 중지 및 제거
        echo -e "${YELLOW}Removing project images...${RESET}"
        docker rm -f $(docker ps -aq --filter "ancestor=fastapi-webhooks-app-web")
        docker rmi fastapi-webhooks-app-web
    fi
    echo -e "${YELLOW}${SEPARATOR}${RESET}"
}

# 애플리케이션 시작 함수
start_application() {
    echo -e "${GREEN}${SEPARATOR}${RESET}"
    echo -e "${GREEN}Starting application with docker-compose...${RESET}"

    docker compose up -d --build

    # 실행 결과 확인
    if [ $? -eq 0 ]; then
        echo -e "${BOLD}${GREEN}=== Application started successfully! ===${RESET}"
        echo -e "${GREEN}API is running at http://localhost:8080${RESET}"
        echo -e "${GREEN}API documentation is available at http://localhost:8080/docs${RESET}"
        echo -e "${GREEN}=== Container Status ===${RESET}"
        docker compose ps
    else
        echo -e "${RED}Error starting application!${RESET}"
        exit 1
    fi
    echo -e "${GREEN}${SEPARATOR}${RESET}"
}

# 메인 스크립트 실행
echo -e "${BOLD}${BLUE}${SEPARATOR}${RESET}"
echo -e "${BOLD}${BLUE}=== Starting deployment process ===${RESET}"
echo -e "${BOLD}${BLUE}${SEPARATOR}${RESET}"

# 기존 리소스 정리
cleanup

# 새로운 애플리케이션 시작
start_application

# 스크립트 종료 시간 기록
echo -e "${BOLD}${BLUE}${SEPARATOR}${RESET}"
echo -e "${BOLD}${BLUE}=== Script completed at $(date -u) ===${RESET}"
echo -e "${BOLD}${BLUE}${SEPARATOR}${RESET}"
