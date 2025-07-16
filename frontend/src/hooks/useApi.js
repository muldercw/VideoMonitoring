import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiEndpoints } from '../utils/api';

// Custom hook for API queries
export const useApiQuery = (key, queryFn, options = {}) => {
  return useQuery(key, async () => {
    const response = await queryFn();
    return response.data;
  }, {
    staleTime: 30000,
    refetchInterval: 60000,
    ...options,
  });
};

// System hooks
export const useSystemStatus = () => {
  return useApiQuery('systemStatus', apiEndpoints.systemStatus, {
    refetchInterval: 30000,
  });
};

export const useSystemMetrics = (hours = 24) => {
  return useApiQuery(['systemMetrics', hours], () => apiEndpoints.systemMetrics(hours));
};

export const useDashboardSummary = () => {
  return useApiQuery('dashboardSummary', apiEndpoints.dashboardSummary, {
    refetchInterval: 30000,
  });
};

// Stream hooks
export const useStreams = () => {
  return useQuery('streams', async () => {
    const response = await apiEndpoints.getStreams();
    return response.data;
  }, {
    staleTime: 30000,
    refetchInterval: 30000,
  });
};

export const useStream = (streamId) => {
  return useApiQuery(['stream', streamId], () => apiEndpoints.getStream(streamId), {
    enabled: !!streamId,
  });
};

export const useStreamAnalytics = (streamId, hours = 24) => {
  return useApiQuery(
    ['streamAnalytics', streamId, hours],
    () => apiEndpoints.getStreamAnalytics(streamId, hours),
    {
      enabled: !!streamId,
    }
  );
};

export const useStreamEvents = (streamId, eventType = null, hours = 24) => {
  return useApiQuery(
    ['streamEvents', streamId, eventType, hours],
    () => apiEndpoints.getStreamEvents(streamId, eventType, hours),
    {
      enabled: !!streamId,
    }
  );
};

// Stream mutations
export const useCreateStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(async (streamData) => {
    const response = await apiEndpoints.createStream(streamData);
    return response.data;
  }, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};

export const useStartStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(async (streamId) => {
    const response = await apiEndpoints.startStream(streamId);
    return response.data;
  }, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('systemStatus');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};

export const useStopStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(async (streamId) => {
    const response = await apiEndpoints.stopStream(streamId);
    return response.data;
  }, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('systemStatus');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};

export const useDeleteStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation(async (streamId) => {
    const response = await apiEndpoints.deleteStream(streamId);
    return response.data;
  }, {
    onSuccess: () => {
      queryClient.invalidateQueries('streams');
      queryClient.invalidateQueries('dashboardSummary');
    },
  });
};