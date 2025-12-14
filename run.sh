#!/bin/bash

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ____  _   _ ____ _____ _   _ ____  "
echo " / ___|| | | |  _ \_   _| \ | |  _ \ "
echo " \___ \| |_| | |_) || | |  \| | |_) |"
echo "  ___) |  _  |  _ < | | | |\  |  _ < "
echo " |____/|_| |_|_| \_\|_| |_| \_|_| \_\\"
echo -e "${NC}"
echo "Starting URL Shortener..."
echo ""

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}Services started!${NC}"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
