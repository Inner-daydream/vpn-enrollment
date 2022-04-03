
serviceName: ${SERVICE_NAME}
containers:
  vpnenrollment:
    command: []
    environment:
      SECRET_KEY: ${SECRET_KEY}
      CLIENT_ID: ${CLIENT_ID}
      CLIENT_SECRET: ${CLIENT_SECRET}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      DYNAMODB_ENDPOINT: ${DYNAMODB_ENDPOINT}
      ENDPOINT: ${ENDPOINT}
      PRIVATE_KEY: ${PRIVATE_KEY}
      PRODUCTION_CONFIG_PATH: /etc/wireguard
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
    image: ${LATEST_VPNENROLLMENT_IMAGE}
    ports:
      "80": HTTP
publicEndpoint:
  containerName: vpnenrollment
  containerPort: 80
  healthCheck:
    healthyThreshold: 2
    intervalSeconds: 20
    path: /
    successCodes: 200-499
    timeoutSeconds: 4
    unhealthyThreshold: 2
