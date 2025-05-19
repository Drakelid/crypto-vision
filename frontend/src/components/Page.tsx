import React, { ReactNode } from 'react';
import { Box, Container, Typography } from '@mui/material';

interface PageProps {
  title: string;
  children: ReactNode;
  actions?: ReactNode;
}

const Page: React.FC<PageProps> = ({ title, children, actions }) => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {title}
        </Typography>
        {actions && <Box>{actions}</Box>}
      </Box>
      {children}
    </Container>
  );
};

export default Page;
