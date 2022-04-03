
serviceName: ${SERVICE_NAME}
containers:
  vpnenrollment:
    command: []
    environment:
      test: test
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
