#!/bin/bash

# 색상 및 스타일 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# 구분선 정의
SEPARATOR="============================================================"

# 환경 설정 (기본값: dev)
ENVIRONMENT=${1:-dev}
ENV_FILE=".env.${ENVIRONMENT}"
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

# 스크립트 실행 시작 시간 기록
echo -e "${BOLD}${CYAN}${SEPARATOR}${RESET}"
echo -e "${BOLD}${CYAN}=== Pension Manager Sync Controller ===${RESET}"
echo -e "${BOLD}${CYAN}=== Script started at $(date '+%Y-%m-%d %H:%M:%S') ===${RESET}"
echo -e "${BOLD}${CYAN}=== Environment: ${ENVIRONMENT} ===${RESET}"
echo -e "${BOLD}${CYAN}=== User: $USER ===${RESET}"
echo -e "${BOLD}${CYAN}${SEPARATOR}${RESET}"

# 환경 파일 및 compose 파일 존재 확인
check_files() {
    echo -e "${BLUE}Checking required files...${RESET}"
    
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}Error: Environment file '$ENV_FILE' not found!${RESET}"
        echo -e "${YELLOW}Please create the environment file or specify correct environment (dev/prod).${RESET}"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}Error: Docker compose file '$COMPOSE_FILE' not found!${RESET}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Environment file: $ENV_FILE${RESET}"
    echo -e "${GREEN}✓ Compose file: $COMPOSE_FILE${RESET}"
}

# 환경변수 로드 및 검증
load_and_validate_env() {
    echo -e "${BLUE}${SEPARATOR}${RESET}"
    echo -e "${BLUE}Loading environment variables...${RESET}"
    
    # 환경변수 로드
    set -a
    source "$ENV_FILE"
    set +a
    
    # 필수 환경변수 검증
    REQUIRED_VARS=("PORT" "HOST_USER" "HOST_WORKSPACE")
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}Error: Required environment variable '$var' is not set in $ENV_FILE${RESET}"
            exit 1
        fi
        echo -e "${GREEN}✓ $var=${!var}${RESET}"
    done
    
    echo -e "${BLUE}${SEPARATOR}${RESET}"
}

# 컨테이너, 볼륨, 이미지 정리 함수
cleanup() {
    echo -e "${YELLOW}${SEPARATOR}${RESET}"
    echo -e "${YELLOW}Cleaning up existing PM Sync Controller resources...${RESET}"
    
    # 프로젝트별 컨테이너 정리
    CONTAINER_NAME="pm_sync_controller_${ENVIRONMENT}"
    
    if [ "$(docker ps -aq --filter "name=${CONTAINER_NAME}")" ]; then
        echo -e "${YELLOW}Stopping and removing PM Sync Controller containers...${RESET}"
        docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down --volumes --remove-orphans
        docker rm -f $(docker ps -aq --filter "name=${CONTAINER_NAME}") 2>/dev/null || true
    fi

    # 잠시 대기하여 리소스가 완전히 해제되도록 함
    echo -e "${YELLOW}Waiting for resources to be released...${RESET}"
    sleep 3

    # 태그가 none인 이미지 제거
    if [ "$(docker images -f "dangling=true" -q)" ]; then
        echo -e "${YELLOW}Removing dangling images...${RESET}"
        docker rmi -f $(docker images -f "dangling=true" -q) 2>/dev/null || true
    fi

    # 프로젝트 관련 이미지 제거 (선택적)
    PROJECT_IMAGE="pm_sync_controller"
    if [ "$(docker images -q "*${PROJECT_IMAGE}*")" ]; then
        echo -e "${YELLOW}Found project images, removing unused ones...${RESET}"
        # 사용 중이지 않은 이미지만 제거
        docker image prune -f --filter="label=project=${PROJECT_IMAGE}" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ Cleanup completed${RESET}"
    echo -e "${YELLOW}${SEPARATOR}${RESET}"
}

# 서비스 상태 확인
check_service_health() {
    echo -e "${BLUE}Checking service health...${RESET}"
    
    # 컨테이너 상태 확인
    if [ "$(docker ps -q --filter "name=pm_sync_controller_${ENVIRONMENT}")" ]; then
        echo -e "${GREEN}✓ Container is running${RESET}"
        
        # API 헬스체크 (포트가 설정되어 있다면)
        if [ ! -z "$PORT" ]; then
            echo -e "${BLUE}Waiting for API to be ready...${RESET}"
            sleep 5
            
            # 간단한 헬스체크
            if curl -f -s "http://localhost:${PORT}/health" >/dev/null 2>&1 || \
               curl -f -s "http://localhost:${PORT}/" >/dev/null 2>&1; then
                echo -e "${GREEN}✓ API is responding${RESET}"
            else
                echo -e "${YELLOW}⚠ API health check failed (this might be normal if no health endpoint exists)${RESET}"
            fi
        fi
    else
        echo -e "${RED}✗ Container is not running${RESET}"
        return 1
    fi
}

# 애플리케이션 시작 함수
start_application() {
    echo -e "${GREEN}${SEPARATOR}${RESET}"
    echo -e "${GREEN}Starting PM Sync Controller (${ENVIRONMENT} environment)...${RESET}"
    echo -e "${GREEN}Command: docker compose --env-file ${ENV_FILE} -f ${COMPOSE_FILE} up -d --build${RESET}"

    # Docker Compose 실행
    docker compose \
        --env-file "$ENV_FILE" \
        -f "$COMPOSE_FILE" \
        up -d --build

    # 실행 결과 확인
    if [ $? -eq 0 ]; then
        echo -e "${BOLD}${GREEN}=== PM Sync Controller started successfully! ===${RESET}"
        
        # 서비스 정보 출력
        if [ ! -z "$PORT" ]; then
            echo -e "${GREEN}🚀 API Server: http://localhost:${PORT}${RESET}"
            echo -e "${GREEN}📚 API Documentation: http://localhost:${PORT}/docs${RESET}"
            echo -e "${GREEN}🔧 ReDoc Documentation: http://localhost:${PORT}/redoc${RESET}"
        fi
        
        echo -e "${GREEN}=== Container Status ===${RESET}"
        docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
        
        # 서비스 헬스체크
        check_service_health
        
        # 로그 확인 안내
        echo -e "${CYAN}=== Useful Commands ===${RESET}"
        echo -e "${CYAN}View logs: docker compose --env-file ${ENV_FILE} -f ${COMPOSE_FILE} logs -f${RESET}"
        echo -e "${CYAN}Stop services: docker compose --env-file ${ENV_FILE} -f ${COMPOSE_FILE} down${RESET}"
        echo -e "${CYAN}Restart: ./run_app.sh ${ENVIRONMENT}${RESET}"
        
    else
        echo -e "${RED}❌ Error starting PM Sync Controller!${RESET}"
        echo -e "${RED}Showing recent logs:${RESET}"
        docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=20
        exit 1
    fi
    echo -e "${GREEN}${SEPARATOR}${RESET}"
}

# 사용법 출력
show_usage() {
    echo -e "${PURPLE}Usage: $0 [environment]${RESET}"
    echo -e "${PURPLE}  environment: dev (default) | prod${RESET}"
    echo -e "${PURPLE}Examples:${RESET}"
    echo -e "${PURPLE}  $0        # Run in development mode${RESET}"
    echo -e "${PURPLE}  $0 dev    # Run in development mode${RESET}"
    echo -e "${PURPLE}  $0 prod   # Run in production mode${RESET}"
}

# 메인 스크립트 실행
main() {
    # 도움말 확인
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    # 환경 검증
    if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
        echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'. Use 'dev' or 'prod'.${RESET}"
        show_usage
        exit 1
    fi

    echo -e "${BOLD}${PURPLE}${SEPARATOR}${RESET}"
    echo -e "${BOLD}${PURPLE}=== Starting PM Sync Controller deployment ===${RESET}"
    echo -e "${BOLD}${PURPLE}${SEPARATOR}${RESET}"

    # 파일 존재 확인
    check_files

    # 환경변수 로드 및 검증
    load_and_validate_env

    # 기존 리소스 정리
    cleanup

    # 새로운 애플리케이션 시작
    start_application

    # 스크립트 종료 시간 기록
    echo -e "${BOLD}${CYAN}${SEPARATOR}${RESET}"
    echo -e "${BOLD}${CYAN}=== Deployment completed at $(date '+%Y-%m-%d %H:%M:%S') ===${RESET}"
    echo -e "${BOLD}${CYAN}=== Environment: ${ENVIRONMENT} ===${RESET}"
    echo -e "${BOLD}${CYAN}${SEPARATOR}${RESET}"
}

# 스크립트 실행
main "$@"